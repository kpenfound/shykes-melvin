from typing import Annotated
from dagger import dag, Doc, Directory, function, Module, object_type


@object_type
class DaggerProgrammer:
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
        ws = dag.module_workspace(language, source_mod_name)

        source_mod_file = await mod.source().directory(".").file(await dag.module_helper().get_sdk_main_file(source_mod_sdk, source_mod_name)).contents()

        # translate the source mod to the target sdk
        work = (
            dag
            .llm()
            .with_module_workspace(ws)
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
        # read the current module
        source_mod_sdk = await mod.sdk().source()
        source_mod_name = await mod.name()

        # write example in the module's same language
        ws = dag.module_workspace(source_mod_sdk, source_mod_name)
        # source_mod_file = await mod.source().directory(".").file(self.getSdkMainFile(source_mod_sdk, source_mod_name)).contents()
        source_mod_schema = await dag.module_helper().get_module_schema(mod)
        example_work = (
            dag
            .llm()
            .with_module_workspace(ws)
            .with_prompt_var("language", source_mod_sdk)
            .with_prompt_var("source_mod_schema", source_mod_schema)
            .with_prompt_file(dag.current_module().source().file("prompt_exampler.txt"))
            .module_workspace()
        )
        return example_work.workspace()
        # # make sure the first example works
        # await example_work.test()
        # example = example_work.workspace()

        # # translate that example to the other languages
        # all_examples = dag.directory().with_directory(f"examples/{source_mod_sdk}", example)

        # for sdk in ["go", "python", "typescript"]: # , "php", "java"]:
        #     if sdk == source_mod_sdk:
        #         continue
        #     translated_example = await self.translate(example, sdk)
        #     all_examples = all_examples.with_directory(f"examples/{sdk}", translated_example)

        # # return the directory including all the examples
        # return all_examples
