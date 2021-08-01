import sys
import pandas as pd

file_path = sys.argv[1]
output_file_name = 'transformed.csv'

try:
    df = pd.read_csv(file_path, header=1)
except FileNotFoundError as e:
    print(e)
else:
    # 前処理としてデシジョンテーブルの縦横を入れ替え、空白を空文字で埋め、値をすべて文字列に変換
    df = df.T.fillna('').astype(str)
    # 変換後のデータを格納するための空のdataframeを作成
    df_transformed = df.iloc[:,0:0].fillna('')

    column_index = -1
    column_header = []
    action_flag = False

    row_name0 = df.index.values[0]
    row_name1 = df.index.values[1]
    row_name2 = df.index.values[2]

    for column_name in df:
        # Y, Nは条件記述部の文字列、Xは動作記述部の文字列に変換
        # 条件記述部が階層で記述されている場合と階層がない場合で変換する文字列を変える
        column_char1 = df.loc[row_name1, column_name]
        column_char2 = df.loc[row_name2, column_name]
        if column_char2 != '':
            replace_char = {column_name:{'Y': column_char2,'N': '', 'X': column_char1}}
        else:
            replace_char = {column_name:{'Y': column_char1,'N': 'NOT ' + column_char1, 'X': column_char1}}
        df.replace(replace_char, inplace=True)

        # 動作部用の列を作成。動作部はこれ以降は列を増やさないためにaction_flagをtrueにする
        if df.loc[row_name0, column_name] == '動作':
            action_flag = True
            column_index = column_index + 1
            df_transformed.loc[:, column_index] = ''
            column_header.append('動作')

        # action_flagがfalse（条件部）の場合は条件が増えるたびにdf_transformedに列を増やして条件の文字列を格納
        # action_flagがtrue（動作部）の場合は列を増やさずにdf_transformedにカンマ区切りで文字列を追記
        if not action_flag:
            if column_char1:
                column_index = column_index + 1
                df_transformed.loc[:,column_index] = ''
                column_header.append(column_char1)
            df_transformed.loc[:,column_index] = df_transformed.loc[:,column_index] + df.loc[:, column_name]
        else:
            df_transformed.loc[:,column_index] = df_transformed.loc[:,column_index] + ', ' + df.loc[:, column_name]
            df_transformed.loc[:,column_index] = df_transformed.loc[:,column_index].str.strip(', ')

    # df_transformedにカラムヘッダを設定し不要な列を削除
    df_transformed.columns = column_header
    df_transformed = df_transformed.drop(df_transformed.index[[0, 1, 2]], axis=0)

    # 結果をcsvファイルに出力
    try:
        df_transformed.to_csv(output_file_name, encoding='utf_8_sig')
        print(df_transformed)
    except PermissionError as e:
        print(e)
        print('If you open the file, please close it.')
