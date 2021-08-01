import sys
import numpy as np
import pandas as pd

file_path = sys.argv[1]
output_file_name = 'checked.csv'

try:
    df = pd.read_csv(file_path, header=0, index_col=0)
except FileNotFoundError as e:
    print(e)
else:
    df = df.fillna('').astype(str)
    col_len = len(df.columns)

    header = ''
    header1 = np.arange(0)
    header2 = np.arange(0)
    size = 0

    # header1にparameterの文字列、header2にvalueの文字列を格納
    for column_name in df:
        df_values = df.loc[:, column_name].drop_duplicates()
        size = size + len(df_values)
        for value in df_values:
            header1 = np.append(header1, column_name)
            header2 = np.append(header2, value)

    # チェック結果格納用のdataframeを作成
    header = [header1, header2]
    df_checked = pd.DataFrame(np.zeros(size * size).reshape(size, size), columns = header, index = header).astype(int)

    while df.columns.size > 1:
        for column_name in df:
            if df.columns.get_loc(column_name) != 0:
                # 組み合わせチェック用のdataframeを作成。0列目とそれ以外の列の2列構成
                df_cheking = df.iloc[:,[0, df.columns.get_loc(column_name)]]
                # 組み合わせチェック用のdataframeの全行を順にチェック
                # df_checkedで該当の組み合わせに対するセルの値を1増やして、該当の組み合わせ数をカウント
                for row in df_cheking.itertuples():
                    df_checked.loc[(df.columns[0], row[1]), (column_name, row[2])] += 1
        # 組み合わせチェックが終わった列は元のdataframeから削除
        df = df.drop(df.columns[0], axis=1)

    df_checked = df_checked + df_checked.T

    # 結果をcsvファイルに出力
    try:
        df_checked.to_csv(output_file_name, encoding='utf_8_sig')
        print(df_checked)
    except PermissionError as e:
        print(e)
        print('If you open the file, please close it.')

