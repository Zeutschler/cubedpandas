# Cubed Pandas Backlog
...last revision: **2024.08.14**

## Release 0.3.0
### Reimplementation of the core functionality
#### ... as related to new context based addressing
- [ ] implement 'by(rows, colums)' feature for `Context` objects to mimic GroupBy functionality over 2 axis.
- [ ] Rewrite documentation based on new syntax
- [ ] Extend Expression Parser to support basic filtering and mathematical operations on `Context` objects.
- [x] Boolean logic for `Contex` objects for advanced filtering. `and` and `or` operators for `Context` objects. `and` as default.
- [x] Allow to set the default measure 
- [x] Filter functions for dimensions: include, exclude, filter, like, regex, etc.
- [x] Filter functions for measures: gt, lt, eq, ne, etc.
- [x] Data Type Validation for columns
- [x] Update/rewrite all tests based on new syntax
 
#### ... as related to clean up and feature consolidation
- [ ] Further Cleanup for Cube object.
      Move all none essential methods, properties and settings to respective properties,
      e.g. `Cube.settings`, `Cube.properties`, `Cube.methods` etc.  
- [ ] Implement `Context.full_address` property returning a dictionary. 

#### ... as related to `Slices`
- [ ] Implement basic slicing functionality.


## Future Releases

Just ideas, not yet decided, scheduled and prioritized.

### New Features:
- [ ] Support for **Linked Cubes** to mimic DWH-style star-schemas.
- [ ] **Custom Business Logic**: Allow users to define custom business logic for measures.
- [ ] **Custom Measures**: Allow users to define custom measures.
- [ ] **Custom Dimensions**: Allow users to define custom *calculated* dimensions.
- [ ] **Custom Members**: Allow users to define custom *calculated* members.

