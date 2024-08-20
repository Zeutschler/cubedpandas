# Cubed Pandas Backlog
...last revision: **2024.08.14**

## Release 0.3.0
### Reimplementation of the core functionality

#### Jupyter Integration
- [ ] check string representations for all objects when in running in Jupyter
- [ ] implement `.head`  and `.tail`methods

#### Writeback and Data Manipulation
- [x] Check, adapt and activate the existing writeback functionality.

#### Analytical Features for Dimensions and Members
- [ ] All member related functions should return a list of the member keys as defined in the dataframe. 
      Not wrapped into a `Member` object.
- [ ] Implement `cdf.product.members` property to return a list of all members for a dimension.
- [x] `top(n)` and `bottom(n)` functions for dimensions, e.g. `cdf.product.top(2)`.
- [ ] `count` property for dimensions, e.g. `cdf.Online.product.count`, to count the number of distinct members.
      The current implementation counts the records for the default measure.

#### ... as related to new context based addressing
- [x] Implement `Context.full_address` property returning a dictionary. 
- [ ] Support callable function to filter Context objects, e.g. `cdf.product.filter(lambda x: x.startswith("A"))`.
- [ ] 'any', 'is_nan', 'is_null', 'is_not_nan', 'is_not_null' functions for measures.
- [ ] implement 'by(rows, colums)' feature for `Context` objects to mimic GroupBy functionality over 2 axis.
- [ ] Rewrite documentation based on new syntax
- [ ] Extend Expression Parser to support basic filtering and mathematical operations on `Context` objects.
- [x] Boolean logic for `Contex` objects for advanced filtering. `and` and `or` operators 
      for `Context` objects,`and` as default.
- [x] Allow to set the default measure 
- [x] Filter functions for dimensions: include, exclude, filter, like, regex, etc.
- [x] Filter functions for measures: gt, lt, eq, ne, etc.
- [x] Data Type Validation for columns
- [x] Update/rewrite all tests based on new syntax
 
#### ... as related to clean up and feature consolidation
- [ ] Further Cleanup and rewrite for Cube, Dimension and Measure object.
      Move all none essential methods, properties and settings to respective properties,
      e.g. `Cube.settings`, `Cube.properties`, `Cube.methods` etc.  


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

