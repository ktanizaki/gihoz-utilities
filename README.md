# Utilities for GIHOZ

テスト技法ツールGIHOZで作成したデータを活用するツール群です。
GIHOZはこちら。
https://www.veriserve.co.jp/gihoz/

## Check combinations of pair-wise testing
GIHOZのペアワイズテストの生成結果をCSVダウンロードして、以下のコマンドを実行してください。checked.csvというファイルに実行結果が出力されます。

``` shell
$ python check_combinations.py <CSV file name>
```

パラメータと値の総当たり表が作成されます。総当たり表は以下の形式で、組み合わせが登場した回数を数字で表しており、組み合わせの網羅度合いを確認できます。

|||パラメータ1||パラメータ2||パラメータ3||
|---|---|---|---|---|---|---|---|
|||値1|値2|値3|値4|値5|値6|
|パラメータ1|値1|0|0|2|1|1|2|
||値2|0|0|1|1|1|1|
|パラメータ2|値3|2|1|0|0|1|2|
||値4|1|1|0|0|1|1|
|パラメータ3|値5|1|1|1|1|0|0|
||値6|2|1|2|1|0|0|

## Generate test cases from a state transition table
状態遷移表（状態×イベント）からテストケースを生成します。GIHOZのWeb APIを利用するため、インターネットに接続できる環境で実行してください。利用手順は以下の通りです。

1. コードの中の `YOUR_PERSONAL_ACCESS_TOKEN` という文字列を、GIHOZで発行したAPIトークンの文字列に置き換えます。

2. 状態遷移表（状態×イベント）のCSVファイルを用意します。形式は下表の通りです。
1行目にイベント名、1列目に遷移前の状態名、交点のセルに遷移後の状態名を入力します。改行は入力しないでください。遷移がないセルは空欄としてください。
たとえば一番右下のセルは、「状態3のときにイベント3が発生すると状態1に遷移する」ということを表現しています。

||イベント1|イベント2|イベント3|
|---|---|---|---|
|状態1|状態2|||
|状態2||状態3||
|状態3|状態2||状態1|

3. 以下のコマンドを実行してください。`desired test case`には`0_switch` `1_switch` `2_switch` `3_switch` `all_transition`のいずれかを指定してください。指定がない場合は`all_transition`を指定したものとしてテストケースを生成します。
生成したテストケースは、`0_switch_test_cases.csv`といったファイル名で保存されます。ファイル名の`0_switch`の部分は`desired test case`で指定した文字列となります。

``` shell
$ python generate_testcases_from_state_transition_table.py <CSV file name> [desired test case]
```

## Transform a decision table to a test cases list
GIHOZのデシジョンテーブルテストで作成した結果をCSVダウンロードして、以下のコマンドを実行してください。transformed.csvというファイルに実行結果が出力されます。

``` shell
$ python transform_decisiontable.py <CSV file name>
```
デシジョンテーブルをテストケースリストに変換します。例えば、以下のようなデシジョンテーブルをGIHOZで作成したとします。

||||1|2|3|4|5|6|7|8|
|---|---|---|---|---|---|---|---|---|---|---|
|条件|会員|通常会員|Y|Y|Y|Y|N|N|N|N|
|||ゴールド会員|N|N|N|N|Y|Y|Y|Y|
||クーポン持参||Y|Y|N|N|Y|Y|N|N|
||サービスタイム||Y|N|Y|N|Y|N|Y|N|
|動作|割引なし|||||X||
||3%割引|||X|X|||||X|
||5%割引||X|||||X|X||
||10%割引||||||X||||
||新クーポン配布|||X||||X|||

transform_decisiontable.pyを実行すると以下の形式で出力されます。

||会員|クーポン持参|サービスタイム|動作|
|---|---|---|---|---|
|1|通常会員|クーポン持参|サービスタイム|5%割引|
|2|通常会員|クーポン持参|NOT サービタイム|3%割引, 新クーポン配布|
|3|通常会員|NOT クーポン持参|サービスタイム|3%割引|
|4|通常会員|NOT クーポン持参|NOT サービスタイム|割引なし|
|5|ゴールド会員|クーポン持参|サービスタイム|10%割引|
|6|ゴールド会員|クーポン持参|NOT サービスタイム|5%割引, 新クーポン配布|
|7|ゴールド会員|NOT クーポン持参|サービスタイム|5%割引|
|8|ゴールド会員|NOT クーポン持参|NOT サービスタイム|3%割引|

リストへの変換のルールは以下の通りです。
* サブ条件（条件の子階層）が存在する場合、「Y」が指定されたサブ条件の名称をリストに反映します
* サブ条件がない場合、「Y」が指定された条件は名称をそのままリストに反映し、「N」が指定された条件は「NOT 名称」をリストに反映します
* 動作に複数の「X」を指定していた場合、動作の名称をカンマ区切りの文字列に結合してリストに反映します