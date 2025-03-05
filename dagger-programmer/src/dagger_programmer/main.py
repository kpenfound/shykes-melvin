from typing import Annotated
from dagger import dag, Doc, Directory, function, Module, object_type

@object_type
class DaggerProgrammer:
    model: Annotated[str | None, Doc("LLM model to use")] = None
    dagger_version: Annotated[str, Doc("version of the dagger CLI to use")] = "latest"
    @function
    async def translate(
        self,
        mod: Annotated[Module, Doc("The dagger module to translate")],
        language: Annotated[str, Doc("The language to translate the module to")],
    ) -> Directory:
        """Returns a dagger module in the specified language translated from the provided module"""
        # read the current module
        source_mod_sdk = await mod.sdk().source()
        source_mod_name = await mod.name()

        # Create a mod/workspace for the translated sdk
        ws = dag.module_workspace(language, source_mod_name, dagger_version=self.dagger_version)

        source_mod_file = await mod.source().directory(".").file(await dag.module_helper().get_sdk_main_file(source_mod_sdk, source_mod_name)).contents()

        # translate the source mod to the target sdk
        work = (
            dag
            .llm(model=self.model)
            .with_module_workspace(ws)
            .with_prompt(await ws.get_sdk_reference(source_mod_sdk))
            .with_prompt(await ws.get_sdk_reference(language))
            .with_prompt_var("language", language)
            .with_prompt_var("source_mod_sdk", source_mod_sdk)
            .with_prompt_var("source_mod_file", source_mod_file)
            .with_prompt_file(dag.current_module().source().file("prompt_translator.txt"))
            .module_workspace()
        )

        # Check again that test passes because LLMs lie
        await work.test()

        # return work output
        return work.workspace()

    @function
    async def write_examples(
        self,
        mod: Annotated[Module, Doc("The dagger module to write examples for")],
    ) -> Directory:
        """Writes examples in all supported languages for the provided module and returns the directory containing them"""
        # write example in the Go
        ws = dag.module_workspace("go", "example", dependencies=[mod.source().directory(".")], dagger_version=self.dagger_version)
        source_mod_schema = await dag.module_helper().get_module_schema(mod)
        example_work = (
            dag
            .llm(model=self.model)
            .with_module_workspace(ws)
            .with_prompt(await ws.get_sdk_reference("go"))
            .with_prompt_var("source_mod_schema", source_mod_schema)
            .with_prompt_file(dag.current_module().source().file("prompt_exampler.txt"))
            .module_workspace()
        )
        # return example_work.workspace()
        # # make sure the first example works
        await example_work.test()
        example = example_work.workspace()
        example_mod = self.convert_example_to_module(example, mod.source().directory("."), "go")

        # translate that example to the other languages
        all_examples = dag.directory().with_directory("examples/go", example_mod)

        for sdk in ["python", "typescript"]: # , "php", "java"]: # started with Go
            translated_example = await self.translate(example_mod.as_module(), sdk)
            translated_mod = self.convert_example_to_module(translated_example, mod.source().directory("."), sdk)
            all_examples = all_examples.with_directory(f"examples/{sdk}", translated_mod)

        # return the directory including all the examples
        return all_examples

    def convert_example_to_module(self, example: Directory, context: Directory, sdk: str) -> Directory:
        """Generates the dagger.json and other files needed for a module"""
        return (
            dag.container()
            .from_("alpine")
            .with_exec(["apk", "add", "curl"])
            .with_env_variable("DAGGER_VERSION", self.dagger_version)
            .with_exec([
                "sh",
                "-c",
                "curl -fsSL https://dl.dagger.io/dagger/install.sh | BIN_DIR=/usr/local/bin sh",
            ])
            .with_directory("/mod", context)
            .with_directory(f"/mod/examples/{sdk}", dag.directory())
            .with_workdir(f"/mod/examples/{sdk}")
            .with_exec(["dagger", "init", "--name", "example", "--sdk", sdk], experimental_privileged_nesting=True)
            .with_exec(["dagger", "install", "../.."], experimental_privileged_nesting=True)
            .with_directory(f"/mod/examples/{sdk}", example)
            .directory(f"/mod/examples/{sdk}")
        )
