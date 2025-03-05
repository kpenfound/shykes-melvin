## Overview

A Dagger Example module is a normal Dagger module that calls the functions of the module you're creating examples for.
An example module should look like any other Dagger module but it showcases how to call the functions of the module you're creating examples for.
By adhering to the following function naming schemes, the functions will be properly associated with the functions
in the module you are creating examples for.

Your import should be "dagger/example/internal/dagger"

## Function naming scheme

If you have a module called 'Foo' and a function called 'Bar', you can create the following functions in your example module:
- A function 'Foo_Baz' will create a top level example for the 'Foo' module called Baz.
- A function 'FooBar' will create an example for function 'Bar'.
- Functions 'FooBar_Baz' will create a Baz example for the function 'Bar'.

## Example reference

Consider the "proxy" module:

```xml
<module name='proxy' description=''>
        <function name='service' description='Get the proxy Service' returns='Service!'>
        </function>
        <function name='withService' description='Add a service to proxy' returns='Proxy!'>
                <arg name='service' type='Service!' description='A content-addressed service providing TCP connectivity.' />
                <arg name='name' type='String!' description='' />
                <arg name='frontend' type='Integer!' description='' />
                <arg name='backend' type='Integer!' description='' />
                <arg name='isTcp' type='Boolean!' description='' />
        </function>
</module>
```

The example module for the proxy module would look like this:

```go
// Proxy examples in Go
package main

import "dagger/example/internal/dagger"

type Example struct{}

// Example for WithService function
func (m *Example) ProxyWithService(service *dagger.Service) *dagger.Service {
	return dag.Proxy().
		WithService(
			service,     // Dagger service to proxy
			"MyService", // Name of the service
			8080,        // Port for the proxy to listen on
			80,          // Port for the proxy to forward to
		).Service()
}

// Example for Service function
func (m *Example) ProxyService(serviceA *dagger.Service, serviceB *dagger.Service) *dagger.Service {
	return dag.Proxy().
		WithService(
			serviceA,   // Dagger service to proxy
			"ServiceA", // Name of the service
			8080,       // Port for the proxy to listen on
			80,         // Port for the proxy to forward to
		).
		WithService(
			serviceB,   // Dagger service to proxy
			"ServiceB", // Name of the service
			8081,       // Port for the proxy to listen on
			80,         // Port for the proxy to forward to
		).
		Service() // Return a Dagger service proxying to multiple services
}
```
