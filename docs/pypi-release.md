# PyPI 发布流程

这个仓库已经配置了三条 GitHub Actions 流水线：

- `CI`: 在 `master` 提交和 Pull Request 上运行测试、构建和 `twine check`
- `Publish TestPyPI`: 手动触发，发布到 TestPyPI 做预发布验证
- `Publish PyPI`: 在推送 `v*` 标签后发布到正式 PyPI

## 一次性配置

### 1. 在 PyPI 创建项目

1. 注册 [PyPI](https://pypi.org/) 和 [TestPyPI](https://test.pypi.org/) 账号
2. 在两个站点都创建 `bookkeeping-bot` 项目名，或者先通过一次手动发布占位

### 2. 配置 Trusted Publisher

分别在 PyPI 和 TestPyPI 中添加 GitHub Trusted Publisher。

建议使用以下配置：

- Owner: `d3lap1ace`
- Repository name: `bookeeping-skills`
- Workflow name:
  - TestPyPI: `publish-testpypi.yml`
  - PyPI: `publish-pypi.yml`
- Environment name:
  - TestPyPI: `testpypi`
  - PyPI: `pypi`

如果你的默认分支、仓库名或工作流文件名不同，需要同步修改 PyPI 上的配置。

### 3. 开启 GitHub Environments

在 GitHub 仓库中创建两个 environments：

- `testpypi`
- `pypi`

你可以给 `pypi` 环境增加保护规则，例如要求手动审批后才允许正式发布。

## 日常流程

### 提交到 master

推送到 `master` 后会自动执行：

1. `CI` 运行测试和构建校验

### 发布到 TestPyPI

当你想先做一次预发布验证时：

1. 更新 [pyproject.toml](../pyproject.toml) 中的 `version`
2. 在 GitHub Actions 页面手动运行 `Publish TestPyPI`

如果版本号没有变化，TestPyPI 会拒绝重复上传，所以每次预发布都需要一个新的版本号。

### 发布正式版本

1. 更新 [pyproject.toml](../pyproject.toml) 里的 `version`
2. 提交并合并到 `master`
3. 打标签并推送：

```bash
git tag v0.1.0
git push origin v0.1.0
```

4. `Publish PyPI` 会自动构建并发布到正式 PyPI

## 本地验证

发布前可以先在本地构建：

```bash
python -m build
```

如果你已经安装了 `pipx`，也可以直接验证 wheel：

```bash
pipx install dist/bookkeeping_bot-0.1.0-py3-none-any.whl
```

## 安装命令

正式发布成功后，用户可以直接安装：

```bash
pipx install bookkeeping-bot
```
