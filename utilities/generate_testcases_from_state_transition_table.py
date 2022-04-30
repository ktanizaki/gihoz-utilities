import sys
import pandas as pd
import json
import requests
import csv

# GIHOZのAPIを利用して、状態遷移表（状態×イベント）から状態遷移テストのテストケースを生成する
def main():
    try:
        # ここにGIHOZで発行したAPIトークンを記載する
        token = 'YOUR_PERSONAL_ACCESS_TOKEN'

        # 第1引数から状態遷移表（状態×イベント）のファイルパスを取得してファイルを読み込み
        file_path = sys.argv[1]
        df = pd.read_csv(file_path, header=0, index_col=0)

        # 第2引数から生成するテストケースの種類を取得して、テストモデルの雛形を生成。指定がない場合は'all_transition'とする。
        if len(sys.argv) >= 3:
            desired_test_case = sys.argv[2]
            if desired_test_case != '0_switch' and desired_test_case != '1_switch' and desired_test_case != '2_switch' and desired_test_case != '3_switch' and desired_test_case != 'all_transition':
                raise ValueError('Please input one of the followings as the second argument: 0_switch, 1_switch, 2_switch, 3_switch, all_transition')
        else:
            desired_test_case = 'all_transition'
        # 第2引数で指定されたテストケースだけ生成したい場合
        test_model_str = '{"test_type":"state_transition","desired_test_case": ["' + desired_test_case + '"],"test_spec_model":{"node_data":[],"link_data":[]}}'
        # 全部のテストケースを生成したい場合
        # test_model_str = '{"test_type":"state_transition","desired_test_case": ["0_switch","1_switch","2_switch","3_switch","all_transition","state_and_event_table","state_and_state_table"],"test_spec_model":{"node_data":[],"link_data":[]}}'
        test_model_json = json.loads(test_model_str)

        # 状態遷移表（状態×イベント）をGIHOZのAPIの入力データ形式（JSON）に変換
        node_data = []
        link_data = []
        for i, state in enumerate(df.index):
            node_data.append(json.loads('{"id": ' + str(i) +',"text": "' + state + '"}'))
            for j, event in enumerate(df.columns):
                if str(df.values[i][j]) != 'nan':
                    link_data.append(json.loads('{"from":' + str(i) + ',"to":' + str(df.index.get_loc(df.values[i][j])) + ',"text":"' + event + '"}'))
        test_model_json['test_spec_model']['node_data'] = node_data
        test_model_json['test_spec_model']['link_data'] = link_data
        #print(json.dumps(test_model_json, indent=2))

        # GIHOZの状態遷移テストのテストケース生成APIにリクエストを送信
        post_url = 'https://gihoz-api.veriserve.co.jp/api/v1/test_cases/state_transition'
        headers = {'Authorization': 'Bearer ' + token}
        response = requests.post(post_url, headers=headers, json=test_model_json)
        test_case_json = json.loads(response.text)
        #print(json.dumps(test_case_json, indent=2))

        # テストケースをCSVファイルに出力
        export_csv(test_case_json, desired_test_case)

    except FileNotFoundError as e:
        print(e)
    except ValueError as e:
        print(e)
    except Exception as e:
        print(e)
        print('An error occurred. Pleas check the input file is correct. The state name / event name may be incorrect or include newline characters.')

# テストケースをcsvファイルに出力する
def export_csv(test_case_json, desired_test_case):
    try:
        # テストケースのJSON全体の中から、desired_test_caseで指定されたテストケースのリストを抽出
        test_case_list = test_case_json['data']['attributes']['test_case_json'][desired_test_case]

        # テストケースのリストをCSVファイルに書き込み
        with open(desired_test_case + '_test_cases.csv', 'w', newline='') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_ALL,delimiter=',')
            writer.writerows(test_case_list)
            print(test_case_list)
            print('These test cases were exported to "' + desired_test_case + '_test_cases.csv".')

    except PermissionError as e:
        # 書き込み対象のCSVファイルがロックされている場合、エラーを出力
        print(e)
        print('If you open "' + desired_test_case + '_test_cases.csv"' + ', please close it.')
    except Exception as e:
        print(e)
        print('Unexpected error occurred.')

if __name__ == '__main__':
    main()