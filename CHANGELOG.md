# CHANGELOG


## v1.4.2 (2025-03-09)

### Bug Fixes

- Add retry logic for API calls
  ([`676078f`](https://github.com/tflagship/pennyworth-slack-bot/commit/676078ff7b7d276ef31128156786089f9c0f6d8f))


## v1.4.1 (2025-03-09)

### Bug Fixes

- Add health check functionality
  ([`7947320`](https://github.com/tflagship/pennyworth-slack-bot/commit/7947320c5d6c36a62c3c12a719ce3b3e48a7fb4a))


## v1.4.0 (2025-03-09)

### Bug Fixes

- Add 'handle_direct_messages' handler for improved DM/private channel responsiveness
  ([`ae86b85`](https://github.com/tflagship/pennyworth-slack-bot/commit/ae86b85b9b61de566935f188c1a344b7aab76039))

- Move 'channel_info_patterns' before standard response
  ([`850d29c`](https://github.com/tflagship/pennyworth-slack-bot/commit/850d29cf26ae68e41509364b7b569be1cf78ea2c))

### Chores

- Update 'LOG_LEVEL' env. variable with 'LOG_LEVEL' repo variable mapping
  ([`0e0f4b9`](https://github.com/tflagship/pennyworth-slack-bot/commit/0e0f4b9e28e1dc5d849b8ad2c0d1804b4d8a2a2c))

- Update example variables for logs
  ([`27a4031`](https://github.com/tflagship/pennyworth-slack-bot/commit/27a4031f25853659edb73a2b6d62c98cc9e27c1b))

- Update logging configuration
  ([`171be55`](https://github.com/tflagship/pennyworth-slack-bot/commit/171be55c5318c6d5508483101e516ae8b7ee31d5))

### Documentation

- Update OAuth scopes and event sunscriptions:
  ([`061365b`](https://github.com/tflagship/pennyworth-slack-bot/commit/061365bf2b58f0f15b0ac452f6b7f697af7badd3))

### Features

- Modify 'get_contextual_response' method to include channel data
  ([`b3ebf84`](https://github.com/tflagship/pennyworth-slack-bot/commit/b3ebf84500bb5b39eca03a8db1378e0031c35fdf))


## v1.3.0 (2025-03-09)

### Chores

- Correct 'GH_TOKEN' env variable ref
  ([`8d7bfce`](https://github.com/tflagship/pennyworth-slack-bot/commit/8d7bfce6642dc7932ee1fc8b22a504dca4d8ea57))

- Fix 'github_token' env variable syntax
  ([`5974f88`](https://github.com/tflagship/pennyworth-slack-bot/commit/5974f88c10682caf85f42a6475ccaebf325aa7f8))

- Update 'semantic-release' cmd auth + workflow
  ([`bfa1be9`](https://github.com/tflagship/pennyworth-slack-bot/commit/bfa1be993cb01a488660ef7757a5e42c28b06cfa))

### Documentation

- Update sem-ver ref
  ([`7dbda5d`](https://github.com/tflagship/pennyworth-slack-bot/commit/7dbda5d1bc9f9199c4f8a96a10b2c8ba7a9a60be))

### Features

- Update user profile settings with 'slack_sdk'
  ([`035e6e0`](https://github.com/tflagship/pennyworth-slack-bot/commit/035e6e0f0eba3b0c4569e1c1ddfdfe0dcf256cd8))


## v1.2.0 (2025-03-08)

### Bug Fixes

- Improve Alfred-style prompts with increased brevity
  ([`fbe74c8`](https://github.com/tflagship/pennyworth-slack-bot/commit/fbe74c8523c71070be4f1ef3d098c112f9f20de1))

### Build System

- Create dockerfile locally
  ([`e7b6563`](https://github.com/tflagship/pennyworth-slack-bot/commit/e7b656351be75a1a19b774a19176a19fa6010c99))

### Chores

- Add improved type annotations to handler methods
  ([`560cd2d`](https://github.com/tflagship/pennyworth-slack-bot/commit/560cd2dbc26286e3e750af955bb47c7e5738eb15))

- Improve Alfred-like responses with requests for both butler refs and Batman comic book refs
  ([`76c422f`](https://github.com/tflagship/pennyworth-slack-bot/commit/76c422f117c2285dcae80196ea5ec654f516fc78))

### Continuous Integration

- Remove dynamic dockerfile creation from workflow
  ([`66e804c`](https://github.com/tflagship/pennyworth-slack-bot/commit/66e804cab629d2b56db05cfbee4aa22fb5659d4a))

### Documentation

- Add more detail to README
  ([`a5e977b`](https://github.com/tflagship/pennyworth-slack-bot/commit/a5e977be7c282a400126c2b2e6e487a104cf7d27))

- Update tag ref
  ([`a90c8bc`](https://github.com/tflagship/pennyworth-slack-bot/commit/a90c8bc5d867147bb6377bfd55d3da2364da8f7f))

### Features

- Add channel conversation context awareness
  ([`0c576fa`](https://github.com/tflagship/pennyworth-slack-bot/commit/0c576fad1bae7edaea7d070951c96010e53c307e))

- Add current time + timezone awareness method
  ([`42381bb`](https://github.com/tflagship/pennyworth-slack-bot/commit/42381bb69da1c6810edf978f05b28b7c368ac932))

### Refactoring

- Move AI Assistant functionality to dedicated module
  ([`9e47ddd`](https://github.com/tflagship/pennyworth-slack-bot/commit/9e47ddd55c0e6ee49005059d2396f5c6eba5e3de))

- Move Trello functionality to dedicated module
  ([`fbd2b30`](https://github.com/tflagship/pennyworth-slack-bot/commit/fbd2b304c21cd4059afe013507191f1f70e0e26c))


## v1.1.0 (2025-03-07)

### Chores

- Add semantic release workflow and config file
  ([`6b4d340`](https://github.com/tflagship/pennyworth-slack-bot/commit/6b4d340e652859339f3aae873c61fafe07f48cac))

### Features

- Add @mentions feature + debug socket mode
  ([`fea019e`](https://github.com/tflagship/pennyworth-slack-bot/commit/fea019eabf68f76c4883cbe3ae74423b68907738))


## v1.0.0 (2025-03-07)

### Bug Fixes

- Import slack_bolt SocketModeHandler package
  ([`91ee68b`](https://github.com/tflagship/pennyworth-slack-bot/commit/91ee68b00fe3d7772fbac23897617d4d22d9b6c6))

- Update 'main' and 'server' modules to match 'bot' updates and adhere to OOP best practices
  ([`b273c31`](https://github.com/tflagship/pennyworth-slack-bot/commit/b273c310272ca5b99867c9c4b50ed519945d3bf2))

- Update app version
  ([`83b687f`](https://github.com/tflagship/pennyworth-slack-bot/commit/83b687f53d3761936e8baa5dc746335ea002ec87))

- Update package versions to better leverage python 3.11 (former: 3.10)
  ([`9153829`](https://github.com/tflagship/pennyworth-slack-bot/commit/91538298d49662e1d76c2e625bf79d050d910c22))

- Update slack_bolt version
  ([`595097f`](https://github.com/tflagship/pennyworth-slack-bot/commit/595097f5a049bf56cc3557dbec6b141f1cacca25))

- Update slack_sdk version
  ([`d2cb9c9`](https://github.com/tflagship/pennyworth-slack-bot/commit/d2cb9c921bafefa2702ddd79821fa1dfd2a2e89f))

- Utilize name standardizer in event handlers function
  ([`f2cfa19`](https://github.com/tflagship/pennyworth-slack-bot/commit/f2cfa19ce4049bac47cc15d4349f06d8714ebe99))

### Chores

- Checkpoint everything
  ([`d8e8eca`](https://github.com/tflagship/pennyworth-slack-bot/commit/d8e8eca20c8f49ce9711aa2d93d96dcf1a195b61))

- Correct 'build_command' value ()
  ([`171584b`](https://github.com/tflagship/pennyworth-slack-bot/commit/171584b71c2ca1dc20a29859a7f3e56a584ca1d6))

- Remove shebang at top of file
  ([`03a9f7a`](https://github.com/tflagship/pennyworth-slack-bot/commit/03a9f7a6c17670152e17106df5800e2947565554))

### Continuous Integration

- Add semantic release workflow and config file
  ([`352f143`](https://github.com/tflagship/pennyworth-slack-bot/commit/352f143fa1c189df14a1a06ada293dcdc9d81d83))

- Correct sem-ver process for docker image build/push/copy
  ([`b538d24`](https://github.com/tflagship/pennyworth-slack-bot/commit/b538d24dd5340c643c2a0c31937388e145c7ce3f))

### Documentation

- Update .gitignore file list
  ([`a625e80`](https://github.com/tflagship/pennyworth-slack-bot/commit/a625e8088a75a25f51e700984952530d8c7bc6f5))

### Features

- Add 'summarize_conversation' function
  ([`1d67fca`](https://github.com/tflagship/pennyworth-slack-bot/commit/1d67fca43796024523fb2056454af548aee059a3))

- Add @mentions feature + debug socket mode
  ([`4c5d6e0`](https://github.com/tflagship/pennyworth-slack-bot/commit/4c5d6e054d99faba4c4292d59c49c90e66f47581))

- Add additional functions for Trello board integrations
  ([`08e89b6`](https://github.com/tflagship/pennyworth-slack-bot/commit/08e89b6d5e06305c6a34f0a28c26b4ff01c4e385))

- Add butler tonality to AI chat features
  ([`9457352`](https://github.com/tflagship/pennyworth-slack-bot/commit/9457352aa29b863ad1923219251a91a1163c57af))

- Add name standardizer helper function
  ([`0066754`](https://github.com/tflagship/pennyworth-slack-bot/commit/0066754b66505695b663023b75eb1d53ce889eed))

- Update slack bot core module with updated features and butler-esque nuances
  ([`3b305cc`](https://github.com/tflagship/pennyworth-slack-bot/commit/3b305cce77c6c95bc09f7aa6d2dbff46aa33f394))
