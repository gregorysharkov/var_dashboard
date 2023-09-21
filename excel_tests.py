import pandas as pd
import xlsxwriter


def main():
    workbook = xlsxwriter.Workbook('template.xlsx')
    sheet = workbook.add_worksheet()
    currency_format = workbook.add_format({"num_format": "$#,##0"})

    data = pd.DataFrame(
        data=[
            ["Apples", 10000, 5000, 8000, 6000],
            ["Pears", 2000, 3000, 4000, 5000],
            ["Bananas", 6000, 6000, 6500, 6000],
            ["Oranges", 500, 300, 200, 700],
        ],
        columns=['fruit', 'q1', 'q2', 'q3', 'q4']
    )
    data['change'] = (data.q4-data.q3)/data.q3

    # options = {
    #     'data': data,
    #     'total_row': 1,
    #     columns = [
    #         {'header': 'product'}
    #     ]
    # }
    sheet.set_column('B:G', 12)
    sheet.write('B1', 'some text')
    sheet.add_table("B3:G7", options={"data": data})
    workbook.close()


if __name__ == '__main__':
    main()
