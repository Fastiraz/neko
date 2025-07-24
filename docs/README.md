# Website

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.

## Installation

```bash
yarn
```

## Local Development

```bash
yarn start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
yarn build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Deployment

Using SSH:

```bash
USE_SSH=true yarn deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> yarn deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.

---

```sh
bunx create-docusaurus@latest neko --typescript --package-manager bun
```

✔ Select a template below... › classic (recommended)
[INFO] Creating new Docusaurus project...
[INFO] Installing dependencies with bun...
[SUCCESS] Created neko.
[INFO] Inside that directory, you can run several commands:

  `bun start`
    Starts the development server.

  `bun run build`
    Bundles your website into static files for production.

  `bun run serve`
    Serves the built website locally.

  `bun run deploy`
    Publishes the website to GitHub pages.

We recommend that you begin by typing:

  `cd neko`
  `bun start`

Happy building awesome websites!
