# DENOG Routing Guide

This guide is intended to act as a reference for best practices in Internet backbone routing. Its goal is to make the Internet more stable, secure and sustainable by educating both new and experienced network engineers.

# Working Group

This guide is edited by the DENOG Working Group for Routing. You don't need to be a member of the working group to contribute to the project.

## Contribute

You can contribute to this routing guide on [github.com/denog/routing-guide/](https://github.com/denog/routing-guide/) using GitHubs issues or pull request features.
We have a [Code of Conduct](https://github.com/denog/routing-guide/blob/main/CODE_OF_CONDUCT.md) as a common ground for collaboration.

For real-time discussions, support, and community interaction, join our [Matrix channel](https://matrix.to/#/#wg-routing-general:denog.de). Everyone interested is welcome to participate!

The DENOG routing WG mailing list can be joined at [Google Groups](https://groups.google.com/a/denog.de/g/denog-wg-routing).

## Deployment

The main branch is deployed to [routing.denog.de](https://routing.denog.de/) the automatically.

## Development

To build the site you need `mkdocs` and the `mkdocs-material` theme installed. For Nix users there is a `shell.nix` file bundled.
On other systems you can use pip to install the dependencies:

```shell
pip3 install -r requirements.txt
```

Then you can use `mkdocs serve` to start a local development server that updates the content automatically.

## Testing

This repo uses [editorconfig-checker](https://github.com/editorconfig-checker/editorconfig-checker) to check for formatting issues when PRs are opened. Use the following commands to install and run editorconfig-checker locally to check for issues before opening a PR:

```shell
pip3 install editorconfig-checker

ec
```

# License

Content is available under the [Creative Commons Attribution License 4.0](https://raw.githubusercontent.com/denog/routing-guide/main/LICENSE.md), unless otherwise stated.
