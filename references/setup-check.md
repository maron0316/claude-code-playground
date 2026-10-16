# 準備の確認

> このキットを使う人は、ターミナルを使わない前提。**デスクトップアプリ（Claude デスクトップアプリ／ChatGPT デスクトップアプリの Codex）で進める。** 本人にコマンドを打たせない。下の「調べること」は、自分（AI）が読み取りだけで行い、結果をかんたんな言葉で伝える。ターミナルの行は、本人がもともとターミナルを使っている場合だけの参考。

## 1. 画面操作（コンピューターの操作）が使えるか

公式ドキュメントで確認した内容（変わることがあるので、つまずいたら公式を見る）:

| 使う場所 | 対応OS | 有効にする方法 |
|---|---|---|
| Claude デスクトップアプリ | macOS・Windows | 設定の General（Desktop app の欄）にある **Computer use** をオンにする |
| Claude Code（ターミナル） | macOS のみ | 会話の中で `/mcp` を実行し、`computer-use` を選んで Enable にする（Claude Code を起動したフォルダごとに1回） |
| Codex（ChatGPT デスクトップアプリ） | macOS・Windows | Codex を開き、Plugins → Computer Use を開いて Install plugin。頼むときに `@Computer` または `@`＋アプリ名を付ける。ターミナルの Codex では画面操作は使えない |

- Claude は **Pro または Max のプラン** が必要（Team・Enterprise では使えない）。研究プレビュー（ページによってはベータと表記）の機能。
- Codex は、Codex が使える ChatGPT のプランで使える。どのプランで画面操作が使えるかは、公式に細かく書かれていない（2026-09-30 確認）。
- macOS では最初に **アクセシビリティ** と **画面収録** の許可を求められる。両方許可する。画面収録を許可したあと、アプリの再起動が必要なことがある。
- 操作するアプリは、最初に許可を求められる（Claude は会話ごと。Codex は「Always allow」を選ぶと次から聞かれない）。編集ソフトは許可してよいが、ターミナル・Finder・システム設定などを許可するときは、何のためかを本人に説明してから。
- 止め方: Claude は、同時に1つの会話しか画面操作を使えない。本人はデスクトップアプリなら停止ボタン、ターミナルなら `Esc` キーで止められる。Codex は、作業中いつでも本人が止めたり操作を代わったりできる。
- スキルの置き場所: Claude は `~/.claude/skills/my-video-editor`（デスクトップアプリの Code タブのローカルの会話で読み込まれる。Cowork やクラウドの会話では読み込まれない）。Codex は `~/.agents/skills/my-video-editor`（ChatGPT デスクトップアプリ・Codex CLI・IDE 拡張で読み込まれる）。
- 画面操作では、スクリーンショットが AI の会社（Anthropic／OpenAI）に送られる。画面に映っている素材の映像も送られることを本人に伝える。
- 出典（Claude・2026-09-28 確認）: https://code.claude.com/docs/en/computer-use ／ https://code.claude.com/docs/en/desktop ／ https://support.claude.com/en/articles/14128542
- 出典（Codex・2026-09-30 確認）: https://learn.chatgpt.com/docs/computer-use ／ https://learn.chatgpt.com/docs/build-skills

**確認の仕方:** 自分がスクリーンショットを撮れるか試す。撮れなければ、本人に上の表を見せて有効にしてもらい、止まる。

**Codex の場合:** 画面操作は、本人が頼む文に `@Computer`（または `@`＋アプリ名）を付けたときに使える。道具が見えなくても「使えない」と決めつけず、本人に「入力欄で `@` を打って Computer を選び、もう一度頼んでください」と伝えて待つ。それでも使えなければ、Plugins → Computer Use が入っているかを確かめてもらう。

## 2. 調べること（読み取るだけ・何も変更しない）

自分（AI）がコマンドを使える環境ならコマンドで、使えなければ画面（Finder／エクスプローラー）を見て調べる。コマンドを使う前に「パソコンの中を見るだけの確認をします。許可の画面が出たら、よければ許可を押してください」と本人に伝える。本人にコマンドを打たせない。

### macOS

| 調べること | コマンドの例 |
|---|---|
| OS の版 | `sw_vers` |
| 入っているアプリ | `ls /Applications ~/Applications` |
| アプリの版 | `mdls -name kMDItemVersion "/Applications/<アプリ名>.app"` |
| 空き容量 | `df -h ~` |

- アプリがフォルダの中に入っているもの（例: `/Applications/<フォルダ名>/<アプリ名>.app`）は、版を調べるときに中の `.app` を指定する。

### Windows（PowerShell）※参考。このキットは Windows では動作を確認していない

| 調べること | コマンドの例 |
|---|---|
| OS の版 | `Get-ComputerInfo -Property OsName,OsVersion` |
| 入っているアプリと版 | 下のコマンド |
| 空き容量 | `Get-PSDrive -PSProvider FileSystem` |

```powershell
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*, HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*, HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Select-Object DisplayName, DisplayVersion | Sort-Object DisplayName
```

- Windows では、ストアから入れたアプリがこの一覧に出ないことがある。見つからなければ、スタートメニューで本人に確かめてもらう。
- 入っているアプリの一覧から、動画編集に使えそうなものを本人に見せ、**どれを使うかは本人が選ぶ**。一覧にないソフトを使いたいと言われたら、場所を教えてもらう。
- 調べた結果は、`my-environment.md` に書く前に本人に見せる。

## 3. 画面を読みやすくする

- Claude の画面操作では、スクリーンショットが縮小されてから届く（公式に記載）。文字が小さくて読めないときは、画面の解像度ではなく、**編集ソフトの中の表示の大きさ**（UIの拡大・パネルの広さ）を本人に変えてもらう。
- 作業中は、関係のないアプリや、見られたくない情報（メール・パスワード管理など）を閉じておいてもらう。
