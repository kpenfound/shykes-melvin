from dagger import function, Module, object_type, TypeDef

@object_type
class ModuleHelper:
    @function
    def get_sdk_main_file(self, sdk: str, name: str) -> str:
        """Get the main SDK file path for the given module name and SDK"""
        return {
            "go": "main.go",
            "python": f"src/{name}/main.py",
            "typescript": "src/index.ts",
            "php": "src/MyModule.php",
            "java": f"src/main/java/io/dagger/modules/{name.lower()}/{name}.java"
        }[sdk]

    @function
    async def get_module_schema(self, mod: Module) -> str:
        """Get the schema of a module represented as an XML string"""
        mod_name = await mod.name()
        mod_description = await mod.description()
        mod_objects = await mod.objects()
        schema = f"\n<module name='{mod_name}' description='{mod_description}'>"
        for obj in mod_objects:
            # just get the main object
            if await self.get_type_name(obj) == mod_name:
                # just get main object functions
                funcs = await obj.as_object().functions()
                for func in funcs:
                    func_name = await func.name()
                    func_description = await func.description()
                    func_return_type = await func.return_type().kind()
                    schema += f"\n\t<function name='${func_name}' description='${func_description}' returns='${func_return_type}'>"
                    func_args = await func.args()
                    for arg in func_args:
                        arg_name = await arg.name()
                        arg_type = await self.get_type_name(arg.type_def())
                        arg_description = await arg.description()
                        schema += f"\n\t\t<arg name='${arg_name}' type='${arg_type}' description='${arg_description}'/>"
                    schema += "\n\t</function>"
        return schema + "\n</module>"

    @function
    async def get_type_name(self, type: TypeDef) -> str:
        """Get the type name of a TypeDef"""
        kind = await type.kind()
        if kind == "object":
            return await type.as_object().name()
        if kind == "scalar":
            return await type.as_scalar().name()
        if kind == "enum":
            return await type.as_enum().name()
        if kind == "input":
            return await type.as_input().name()

        return "UNKNOWN"
