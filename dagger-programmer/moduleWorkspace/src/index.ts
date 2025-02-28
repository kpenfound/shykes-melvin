/**
 * A generated module for DagWorkspace functions
 */
import {
  Container,
  dag,
  Directory,
  object,
  func,
  ReturnType,
} from "@dagger.io/dagger";

@object()
export class ModuleWorkspace {
  /*
   * The workspace directory
   */
  @func()
  workspace: Directory;
  sdk: string;
  name: string;
  daggerVersion: string;

  constructor(
    /*
     * module SDK
     */
    sdk: string,
    /*
     * module name
     */
    name: string,
    /*
     * Dagger Version
     */
    daggerVersion = "latest",
    /*
     * Workspace directory
     */
    workspace?: Directory,
  ) {
    this.sdk = sdk;
    this.name = name;
    this.daggerVersion = daggerVersion;
    this.workspace = workspace ?? dag.directory();
  }
  /**
   * Writes the module code to the workspace
   * @param content The updated module code
   */
  @func()
  async write(content: string): Promise<ModuleWorkspace> {
    // NOTE: constraining this to the default file path for now to keep things simple
    // To develop module examples or more complicated modules, this will need to be unlocked
    this.workspace = this.workspace.withNewFile(
      await dag.moduleHelper().getSdkMainFile(this.sdk, this.name),
      content,
    );
    return this;
  }

  /**
   * Reads the module code from the workspace
   */
  @func()
  async read(): Promise<string> {
    return await this.workspace
      .file(await dag.moduleHelper().getSdkMainFile(this.sdk, this.name))
      .contents();
  }

  /**
   * Test if a module works by outputting the module functions
   */
  @func()
  async test(): Promise<string> {
    const dagger = await this.daggerCommand();
    const functions = dagger.withExec(["/usr/local/bin/dagger", "functions"], {
      experimentalPrivilegedNesting: true,
      expect: ReturnType.Any,
    });
    if ((await functions.exitCode()) != 0) {
      return await functions.stderr();
    }
    return await functions.stdout();
  }

  /**
   * Get SDK reference information for developing with a Dagger SDK
   * @param sdk Dagger SDK language to get reference for
   */
  @func()
  async getSdkReference(sdk: string): Promise<string> {
    const daggerDocs = dag
      .git("https://github.com/dagger/dagger")
      .head()
      .tree()
      .directory("docs/current_docs/");

    // Messing around with changing which snippets are included. Dont want to overload the LLM with too much info
    const snippets: { [key: string]: string } = {
      // "multi stage build": "/cookbook/snippets/builds/multi-stage-build",
      // "cache volumes": "/cookbook/snippets/builds/cache",
      // "secret variables": "/cookbook/snippets/secret-variable",
      "bind services to containers": "/api/snippets/services/bind-services",
      // "expose services to the host": "/api/snippets/services/expose-dagger-services-to-host",
    };

    // FIXME: ideally cookbook snippets would follow module structure too
    const snippetSdkPaths: { [key: string]: string } = {
      go: "main.go",
      python: "main.py",
      typescript: "index.ts",
      php: "src/MyModule.php",
      java: "src/main/java/io/dagger/modules/mymodule/MyModule.java",
    };

    // TODO: also include full sdk reference?
    let reference = `Reference for using Dagger with the ${sdk} SDK\n`;
    reference += `\n
    Assume 'dag' is available globally.
    Object types directly translate to struct types, and have methods for each field.

    <go>
    dag.Container(). // *Container
        WithExec([]string{"sh", "-c", "echo hey > ./some-file"}). // *Container
        File("./some-file") // *File
    </go>

    Calling a method that returns an object type is always lazy, and never returns
    an error:

    <go>
    myFile := dag.Container(). // *Container
        WithExec([]string{"sh", "-c", "echo hey > ./some-file"}). // *Container
        File("./some-file") // *File
    </go>
    \n`;
    reference += `The relevant code for a ${sdk} SDK module is at "${await dag.moduleHelper().getSdkMainFile(sdk, "{module_name}")}"\n`;
    for (const snippet in snippets) {
      const code = await daggerDocs
        .file(`${snippets[snippet]}/${sdk}/${snippetSdkPaths[sdk]}`)
        .contents();
      reference += `\n${snippet}:\n<module>\n${code}\n</module>\n`;
    }
    return reference;
  }

  /**
   * Get reference information on writing examples for a dagger module of a given SDK
   * @param sdk Dagger SDK language to get example reference for
   */
  @func()
  async getExamplesReference(sdk: string): Promise<string> {
    const referenceSnippet = await dag
      .git("https://github.com/kpenfound/dagger-modules")
      .head()
      .tree()
      .directory("proxy/examples")
      .directory(sdk)
      .file(await dag.moduleHelper().getSdkMainFile(sdk, "proxy"))
      .contents();
    const exampleIntro = `
A Dagger Example module is a normal Dagger module that calls the functions of the module you're creating examples for.
An example module should look like any other Dagger module but it showcases how to call the functions of the module you're creating examples for.
By adhering to the following function naming schemes, the functions will be properly associated with the functions
in the module you are creating examples for.
`;
    const exampleReference: { [key: string]: string } = {
      go: `
If you have a module called 'Foo' and a function called 'Bar', you can create the following functions in your example module:
- A function 'Foo_Baz' will create a top level example for the 'Foo' module called Baz.
- A function 'FooBar' will create an example for function 'Bar'.
- Functions 'FooBar_Baz' will create a Baz example for the function 'Bar'.
     `,
      python: `
If you have a module called 'foo' and a function called 'bar', you can create the following functions in your example module:
- A function 'foo__baz' will create a top level example for the 'foo' module called baz.
- A function 'foo_bar' will create an example for function 'bar'.
- Functions 'foo_bar__baz' will create a baz example for the function 'bar'.
note:
Python function names in example modules use double underscores ('__') as separators since by convention, Python uses single underscores to represent spaces in function names (snake case).
    `,
      typescript: `
If you have a module called 'foo' and a function called 'bar', you can create the following functions in your example module:
- A function 'foo_baz' will create a top level example for the 'foo' module called baz.
- A function 'fooBar' will create an example for function 'bar'.
- Functions 'fooBar_baz' and will create a baz example for the function 'bar'.
    `,
      //       shell: ` // not used yet
      // A Shell example must be a shell script located at '/examples/shell' within the module you're creating examples for.
      // If you have a module called 'foo' and a function called 'bar', you can create the following script in your example directory:
      // - A file 'foo_baz.sh' will create a top level example for the 'foo' module called baz.
      // - A file 'foo_bar.sh' will create an example for function 'bar'.
      // - Files 'foo_bar_baz.sh' and will create a baz example for the function 'bar'.
      //     `,
    };

    return `${exampleIntro}\n${exampleReference[sdk]}\n\nThe following is an example module for the Proxy module:\n<example>${referenceSnippet}\n</example>\n`;
  }

  // Helper to get a container that can execute dagger commands on our module
  async daggerCommand(): Promise<Container> {
    return dag
      .container()
      .from("alpine")
      .withExec(["apk", "add", "curl"])
      .withEnvVariable("DAGGER_VERSION", this.daggerVersion)
      .withExec([
        "sh",
        "-c",
        "curl -fsSL https://dl.dagger.io/dagger/install.sh | BIN_DIR=/usr/local/bin sh",
      ])
      .withWorkdir("/mod")
      .withExec(["dagger", "init", "--name", this.name, "--sdk", this.sdk], {
        experimentalPrivilegedNesting: true,
      })
      .withFile(
        await dag.moduleHelper().getSdkMainFile(this.sdk, this.name),
        this.workspace.file(
          await dag.moduleHelper().getSdkMainFile(this.sdk, this.name),
        ),
      );
  }
}
