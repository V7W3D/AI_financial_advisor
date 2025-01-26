from PyPDF2 import PdfReader

reader = PdfReader("quick-ticker-symbol-list.pdf")
ticker_info = open("ticker_info.csv", "a+")
ticker_info.write("ticker, company_name\n")

for i, page in enumerate(reader.pages):
    lines = page.extract_text().strip().split('\n')
    for l in lines:
        if i == 0 and not l.startswith("COMS"):
            continue
        ticker = l.strip().split(' ')
        ticker_info.write(ticker[0]+",")
        for s in ticker[1:]:
            ticker_info.write(" " + s)
        ticker_info.write('\n')

ticker_info.close()
