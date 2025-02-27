from typing import Annotated
from dagger import dag, Doc, Directory, function, object_type


@object_type
class DaggerProgrammer:
    @function
    async def translate(
        self,
        mod: Annotated[Directory, Doc("The dagger module to translate")],
        language: Annotated[str, Doc("The language to translate the module to")],
        subpath: Annotated[str, Doc("The path to the module in the git repository")] = ""
    ) -> Directory:
        """Returns a dagger module in the specified language translated from the provided module"""

        source_mod_sdk = await mod.as_module().sdk().source()
        source_mod_name = await mod.as_module().name()

        # Create a mod/workspace for the translated sdk
        ws = dag.module_workspace(language, source_mod_name)
        main_file_paths = {
            "go": "main.go",
            "python": f"src/{source_mod_name}/main.py",
            "typescript": "src/index.ts",
            "php": "src/MyModule.php",
            "java": "src/main/java/io/dagger/modules/mymodule/MyModule.java"
        }
        source_mod_file = await mod.file(main_file_paths[source_mod_sdk]).contents()

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
    ) -> Directory:
        return await dag.directory()
