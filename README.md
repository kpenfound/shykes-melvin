# Build AI agents with Dagger

## Overview

Dagger is best known for [making CI less terrible](https://docs.dagger.io/#what-problem-does-dagger-solve),
by transforming a mess of artisanal build scripts into clean containerized functions that can run anywhere.

But Dagger is actually a complete runtime and programming environment for distributed applications,
with unique features such as *repeatability*, *caching*, *tracing*, *platform independence*, and a [growing cross-language ecosystem](https://daggerverse.dev).

Besides complex build and test workflows, these features are **perfect for running AI agents**.

This repository explores how and why to use Dagger to build AI agents.

## What is Dagger?

Dagger is a new kind of runtime and programming environment for distributed applications, by the creators of Docker.

Dagger is open-source, and can be installed on any machine that can run Linux containers.
This includes Mac and Windows machines with a Docker-compatible tool installed.

It builds on familiar, proven technology such as [containers](https://github.com/opencontainers/runc),
[DAG engines](https://github.com/moby/buildkit) and [GraphQL](https://graphql.org), and integrates them
into a development experience that emphasizes *simplicity*, *speed* and *repeatability*.

- *Simplicity*: quality software is built from simple components, just like Lego bricks.
- *Speed*: success requires rapid iteration. The faster one can iterate, the faster one can improve.
- *Repeatability*: when components can be trusted to consistently produce the same results under the same conditions, one can build more powerful software, faster.

As we will see, these principles apply to both *complex builds* and *complex AI workflows*.

## Building AI agents with Dagger

Dagger's module system allows implementing agentic features as modular components that you can integrate into your application, or use individually.

Each module has the following features:

- Runs in containers, for maximum portability and reproducibility
- Can be run from the command-line, or programmatically via an API
- Generated bindings for Go, Python, Typescript, PHP (experimental), Java (experimental), and Rust (experimental).
- End-to-end tracing of prompts, tool calls, and even low-level system operations. 100% of agent state changes are traced.
- Cross-language extensions. Add your own modules in any language.
- Platform-independent. No infrastructure lock-in! Runs on any hosting provider that can run containers.

Dagger and your IDE are the only dependency for developing and running these modules.
The entire environment is containerized, for maximum portability.

## Community

Building AI agents on Dagger is an exciting new use case, *that still has rough edges*. We strongly recommend [joining our Community discord](https://discord.gg/KK3AfBP8Gw).
The Dagger community is very welcoming, and will be happy to answer your questions, discuss your use case ideas, and help you get started.

Do this now! It will make the rest of the experience more productive, and more fun.

See also [this Twitter thread](https://x.com/solomonstre/status/1891205257516003344) for examples, discussions and demos.

## Examples

The repository includes several examples of Dagger modules with agentic capabilities, which you can use as inspiration.

- [toy-programmer](./toy-programmer): a very, very simple programmer micro-agent for demo purposes
- [melvin](./melvin): Melvin is [Devin](https://devin.ai)'s little cousin 😄. An experimental open-source coding agent, made of small composable modules rather than one monolithic app.
- [multiagent](./multiagent-demo): a demo using multiple LLMs to solve a problem
- [github-go-coder](./github-go-coder): a Go programmer micro-agent that receives assignments from GitHub issues and creates PRs with it's solutions

## Initial setup

### 1. Install Dagger

*Note: the latest version is `0.17.0-llm.3`. It was released on Feb 21 2025. If you are running an older build, we recommend upgrading.*

You will need a *development version* of Dagger which adds native support for LLM prompting and tool calling.

Once this feature is merged (current target is 0.17), a development build will no longer be required.

Install the development version of LLM-enabled Dagger:

```console
curl -fsSL https://dl.dagger.io/dagger/install.sh | DAGGER_VERSION=0.17.0-llm.3 BIN_DIR=/usr/local/bin sh
```

You can adjust `BIN_DIR` to customize where the `dagger` CLI is installed.

Verify that your Dagger installation works:

```console
$ dagger -c version
v0.17.0-llm.3
```

### 2.Configure LLM endpoints

Dagger uses your system's standard environment variables to route LLM requests. Currently these variables are supported:

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`
- `ANTHROPIC_API_KEY`
- `ANTHROPIC_BASE_URL`
- `ANTHROPIC_MODEL`

Dagger will look for these variables in your environment, or in a `.env` file in the current directory (`.env` files in parent directories are not yet supported).

#### Using with Ollama

You can use Ollama as a local LLM provider. Here's how to set it up:

1. Install Ollama from [ollama.ai](https://ollama.ai)

2. Start Ollama server with host binding:

```shell
OLLAMA_HOST="0.0.0.0:11434" ollama serve
```

3. Get your host machine's IP address:

On macOS / Linux (modern distributions):

```shell
ifconfig | grep "inet " | grep -v 127.0.0.1
```

On Linux (older distributions):

```shell
ip addr | grep "inet " | grep -v 127.0.0.1
```

This step is needed because our LLM type runs inside the engine and needs to reach your local Ollama service. While we're potentially exploring the implementatin of automatic tunneling, for now you'll need to use your machine's actual IP address instead of localhost to allow the containers to communicate with Ollama.

4. Configure the following environment variables (replace `YOUR_IP` with the IP address from step 3):

```plaintext
OPENAI_API_KEY="nothing"
OPENAI_BASE_URL=http://YOUR_IP:11434/v1/
OPENAI_MODEL=llama3.2
```

For example, if your IP is 192.168.64.1:
```plaintext
OPENAI_API_KEY="nothing"
OPENAI_BASE_URL=http://192.168.64.1:11434/v1/
OPENAI_MODEL=llama3.2
```

5. Pull some models to your local Ollama service:

```shell
ollama pull llama3.2
```

Note that to successfully give the LLM Dagger's API to use as a tool, the model should support tools.
Here's a list curated by Ollama of models that support tools: [Ollama models supporting tools](https://ollama.com/search?c=tools)

## Run modules from the command-line

Use the `dagger` CLI to load a module and call its functions.

For example, to use the `toy-programmer` module:

```console
dagger -m ./toy-programmer
```

Then, run this command in the dagger shell:

```
.help
```

This prints available functions. Let's call one:

```
go-program "develop a curl clone" | terminal
```

This calls the `go-program` function with a description of a program to write, then runs the `terminal` function on the returned container.

You can use tab-completion to explore other available functions.

### Integrate Dagger into your application

You can embed Dagger modules into your application.
Supported languages are Python, Typescript, Go, Java, PHP - with more language support under development.

1. Initialize a Dagger module at the root of your application.
This doesn't need to be the root of your git repository - Dagger is monorepo-ready.

```console
dagger init
```

2. Install the modules you wish to load

For example, to install the toy-workspace module:

```console
dagger install github.com/dagger/agents/toy-workspace
```

3. Install a generated client in your project

*TODO: this feature is not yet merged in a stable version of Dagger*

This will configure Dagger to generate client bindings for the language of your choice.

For example, if your project is a Python application:

```console
dagger client install python
```

4. Re-generate clients

*TODO: this feature is not yet merged in a stable version of Dagger*

Any time you need to re-generate your client, run:

```console
dagger client generate
```
