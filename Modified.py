from paddleocr import PaddleOCR
import pandas as pd
import os
import re
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed


logging.getLogger("ppocr").setLevel(logging.ERROR)


def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]


def extract_receipt_data(text):
    code_pattern = r'([A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4})'
    code_match = re.search(code_pattern, text)
    twelve_digit_code = code_match.group(1).replace(
        ' ', '').strip() if code_match else "Code not found"

    lines = text.splitlines()
    lines_lower = [line.lower() for line in lines]

    total_patterns = [
        # OUT + vat/inc combinations
        r'out.*total.*(?:vat|inc)',
        r'out.*(?:vat|inc)',

        # Total + vat/inc combinations but excluding subtotal
        r'(?<!sub)total.*(?:vat|inc)',
        r'(?<!sub)tota.*(?:vat|inc)',

        # IN + vat/inc combinations
        r'in.*(?:total|tota).*(?:vat|inc)',
        r'(?:total|tota).*in.*(?:vat|inc)',
        r'in.*(?:vat|inc)',

        # Simpler patterns but explicitly excluding subtotal
        r'(?<!sub)total\s*\(incl\s*vat\)',
        r'(?<!sub)total\s*incl\s*vat\)',
        r'out\s*total',
        r'in\s*total',
        r'(?<!sub)t[o0]ta[l1i]'
    ]

    in_patterns = [r'in.*(?:total|tota)',  r'in\s*total']
    out_patterns = [r'out.*(?:total|tota)',
                    r'(?:total|tota).*out', r'out\s*total']

    potential_total_lines = []
    for i, line_lower in enumerate(lines_lower):
        if 'subtotal' in line_lower or 'subt' in line_lower:
            continue

        for pattern in total_patterns:
            if re.search(pattern, line_lower):
                potential_total_lines.append(i)
                break

    def find_price(line):
        price_match = re.search(r'(\d+\.\d{2})', line)
        if price_match:
            return price_match.group(1).strip()
        colon_match = re.search(r'(\d+):(\d{2})', line)
        if colon_match:
            return f"{colon_match.group(1)}.{colon_match.group(2)}".strip()
        simple_match = re.search(r'^\s*(\d+)\s*$', line)
        if simple_match:
            return f"{simple_match.group(1)}.00".strip()
        return None

    price = "Price not found"
    price_type = "Unknown"

    if potential_total_lines:
        for idx in potential_total_lines:
            line_lower = lines_lower[idx]

            # Check if it's an IN or OUT total
            is_in = any(re.search(pattern, line_lower)
                        for pattern in in_patterns)
            is_out = any(re.search(pattern, line_lower)
                         for pattern in out_patterns)

            if is_in:
                current_price_type = "In Total"
            elif is_out:
                current_price_type = "Out Total"
            else:
                current_price_type = "Unknown"

            search_order = [idx, idx+1, idx+2, idx-1,
                            idx+3, idx-2, idx+4, idx-3, idx+5, idx+6]
            for search_idx in search_order:
                if 0 <= search_idx < len(lines):
                    if 'subtotal' in lines_lower[search_idx]:
                        continue
                    found_price = find_price(lines[search_idx])
                    if found_price:
                        price = found_price
                        price_type = current_price_type
                        break
            if price != "Price not found":
                break

    if price == "Price not found":
        for i, line in enumerate(lines):
            if 'subtotal' in lines_lower[i]:
                continue

            found_price = find_price(line)
            if found_price:
                price = found_price
                break

    return twelve_digit_code, price, price_type


ocr = PaddleOCR(use_angle_cls=True, lang='en')

# Process a single image and return all required info


def process_image(image_path):
    file_name = os.path.basename(image_path)

    results = ocr.ocr(image_path, cls=True)
    all_text = "\n".join([line[1][0]
                         for line in results[0]]) if results[0] else ""

    code, price, price_type = extract_receipt_data(all_text)
    code_parts = code.split('-')
    if code.lower() == 'code not found':
        code_parts = ['Code not found']*3
    code_parts[0] = code_parts[0].replace(' ', '').strip()
    code_parts[1] = code_parts[1].replace(' ', '').strip()
    code_parts[2] = code_parts[2].replace(' ', '').strip()
    print(f"--- {file_name} ---")
    return [file_name, code_parts, price, price_type]

# Main function


def main():
    base_folder_path = 'Enhanced'
    MAX_COWORKERS = 6
    if not os.path.exists('Threads.txt'):
        with open('Threads.txt', 'w') as f:
            f.write(str(MAX_COWORKERS))
        print(f"Created Threads.txt with {MAX_COWORKERS} threads.")
    else:
        with open('Threads.txt', 'r') as f:
            MAX_COWORKERS = int(f.read())
        print(f"Using {MAX_COWORKERS} threads from Threads.txt.")

    for index, filename in enumerate(os.listdir(base_folder_path)):
        new_name = f"{index+1}.jpg"
        if not os.path.exists(os.path.join(base_folder_path, new_name)):
            os.rename(os.path.join(base_folder_path, filename),
                      os.path.join(base_folder_path, new_name))

    supported_exts = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']

    image_files = [f for f in os.listdir(base_folder_path) if os.path.splitext(f)[
        1].lower() in supported_exts]
    image_paths = [os.path.join(base_folder_path, img) for img in image_files]

    output_excel_path = f"ocr_results.xlsx"
    all_data = []

    with ProcessPoolExecutor(max_workers=MAX_COWORKERS) as executor:
        future_to_path = {executor.submit(
            process_image, path): path for path in image_paths}
        for i, future in enumerate(as_completed(future_to_path), 1):
            try:
                result = future.result()
                final_result = [result[0], result[1][0], result[1]
                                [1], result[1][2], result[2], result[3]]
                print(f"[OK] Processed {result[0]} ({i}/{len(image_paths)})")
                all_data.append(final_result)
            except Exception as e:
                print(f"[ERROR] Error processing {future_to_path[future]}: {e}")

    if all_data:
        df = pd.DataFrame(all_data, columns=[
                          "Filename", "Part 1", "Part 2", "Part 3", "Price", "Price Type"])
        df['sort_key'] = df['Filename'].apply(natural_sort_key)
        df = df.sort_values(by='sort_key').drop('sort_key', axis=1)

        try:
            df.to_excel(output_excel_path, index=False)
            print(f"\n[DONE] All {len(all_data)} images processed and saved to {output_excel_path}")
        except PermissionError:
            fallback_path = "ocr_results_latest.xlsx"
            df.to_excel(fallback_path, index=False)
            print(f"\n[WARNING] {output_excel_path} was locked. Saved results to {fallback_path} instead.")
    else:
        print("\n[DONE] No data to save.")


if __name__ == "__main__":
    main()
