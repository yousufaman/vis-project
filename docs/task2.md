
---
# Task 2: Topology-Based Visualization with Contour Trees

## Introduction: Merge Trees

Many scientific datasets are defined as scalar fields: for every point in a 2D or 3D domain, the dataset stores a single value such as temperature, pressure, density, concentration, or intensity.
Typical visualization methods for this type of data include, for example, isosurfaces or volume rendering.
However, complex scalar fields often complicate analysis, both in terms of manual inspection (for example through occlusion) as well as automated processing (for example through prohibitively large datasets).
In particular 3D scalar fields suffer from occlusion and high data size and complexity.
To accommodate this, topological data analysis provides tools to derive abstract representation of scalar data, which help to reduce visual, structural, and computational complexity.

Two estalished examples for such abstractions are the merge tree and the contour tree.
The contour tree has its roots in the concept of the Reeb graph, introduced by Georges Reeb in 1946, which captures the connectivity of level sets of a scalar function on a manifold.
For simply connected domains, the Reeb graph reduces to a tree structure known as the contour tree, making it particularly suitable for the analysis and visualization of scalar fields in scientific computing.

Merge trees, on the other hand, emerged primarily as an algorithmic tool for the efficient computation of contour trees.
A merge tree tracks the evolution of connected components of sublevel (join tree) or superlevel (split tree) sets as the scalar value changes, encoding the hierarchical relationships between critical points such as minima, maxima, and saddles.
By combining the information from join and split trees, the contour tree provides a complete description of the topological changes of level sets.

Summarizing scalar fields through these topological descriptors, facilitates tasks such as feature identification, segmentation, simplification, and comparative analysis.
Their compact representation makes them particularly suitable for interactive visualization and efficient data processing.
This project focuses on the implementation and visualization of merge trees and contour trees, emphasizing their theoretical foundations, algorithmic construction, and practical application to scalar field data.



### Suggested Reading

1. Hamish Carr, Jack Snoeyink and Ulrike Axen. [Computing contour trees in all dimensions](https://dl.acm.org/doi/10.5555/338219.338659)
   This is the seminal Merge Tree and Contour Tree paper and the most important starting point for the project.
   
2. Kitware. [The VTK User's Guide](https://vtk.org/vtk-users-guide/) and the VTK textbook [The Visualization Toolkit: An Object-Oriented Approach to 3D Graphics](https://vtk.org/vtk-textbook/).  
   These are especially relevant for understanding how isosurface extraction fits into the VTK pipeline model and how existing VTK filters are structured.

3. Hamish Carr and Jack Snoeyink. [Flexible Isosurfaces: Simplifying and Displaying Scalar Topology Using the Contour Tree](https://cdr.lib.unc.edu/downloads/3484zs41k).
   Recommended as a follow-up reading if you want to understand how contour trees can be used beyond pure computation: as an interface for contour exploration, simplification, and the computation of geometric properties attached to tree arcs.

4. Christian Heine, Dominic Schneider, Hamish Carr and Gerik Scheuermann. [Drawing Contour Trees in the Plane](https://dl.acm.org/doi/10.1109/TVCG.2010.270)
   This is a very good follow-up reading for the layout task. It focuses specifically on how contour trees can be drawn clearly in 2D and discusses aesthetic criteria for readable layouts.

As you read, focus on the following questions:
- What exactly is represented by a merge tree, a split tree, and a contour tree, and how do these structures differ?
- How do critical points and the connectivity of sublevel and superlevel sets determine the structure of the resulting tree?
- How the edges of merge trees and contour trees relate to simplices of the input domain?
- How can contour trees be used not only as abstract summaries of topology, but also as practical tools for segmentation, simplification, and contour/isovalue exploration?

---

## Task 1: Implement the merge tree computation

As merge trees form the foundation of modern, efficient methods for contour tree computation, we begin with this abstraction.
Carr et al. introduced the merge tree as a means to compute contour tree in their paper [Computing contour trees in all dimensions](https://dl.acm.org/doi/10.5555/338219.338659).
As the first task, implement a VTK filter (`vtkVISMergeTree`) that computes merge trees using the algorithm by Carr et al., based on sorting the vertices of a scalar field and a union find data structure.

By the end of this task, you should have a reusable VTK filter that can be called from Python, inserted into a standard VTK pipeline, and used as the foundation for later extensions, comparisons, and performance studies.
Your implementation should be able to compute both join trees and split trees, for example by using a parameter to control the direction of the merge tree computation.
The output should be a tree structure that captures the critical points and their relationships based on the input scalar field.

### Hints

- You are free to produce any vtk type as output format, however, we recommend `vtkGraph`.

- Recall that contour trees are only well-defined on simply connected domains. Accordingly, you are allowed to assume that the input scalar field is defined on a regular grid, but you should not assume any specific resolution. The filter should work for any 2D or 3D regular grid.

- What preprocessing step are necessary when working with regular grids? For example, do regular grids define simplicial complexes, and if not, how can you convert them into a format that does?

## Task 2: Merge tree examples

To properly inspect the resulting tree, specific layout methods are needed.
We postpone the implementation of such methods for now and focus more on formal or empirical aspects of the resulting tree.
If you are using `vtkGraph` as output format, you can use `vtkGraphLayoutView` to visualize the resulting tree.
We will discuss layout strategies in Task 5, but for now, the goal is to understand the structure of the resulting tree and to validate that it matches the expected structure based on the definition of the input scalar field.

Towards this, we define synthetic scalar fields (in vtk format) for which the number of critical points and the structure of the merge tree can be easily predicted. 
We use this example to validate the merge tree implementation from Task 1. 
In particular, we check that the number of critical points and the structure of the resulting tree match the expectations based on the definition of the scalar field.

As a first step, design a simple scalar field that produces a trivial merge tree: a single minimum and a single maximum with an edge between them.

Then, design a more complex scalar field that produces a non-trivial merge tree with multiple minima, maxima, and saddles.

Use these examples to test your implementation and to understand how the structure of the merge tree reflects the topological features of the scalar field.
Your example should be scalable in the sense that you can easily modify it to produce more or fewer critical points and a more or less complex tree structure.

Lastly, define a scalar field that produces merge trees of maximim size, i.e. a merge tree with as many nodes and arcs as possible for a given resolution of the input domain.

Use these datasets with varying output complexity to study the runtime behavior of the implemented algorithm.
Show (for example using simple plots) how the runtime scales with the input size on each of the three classes of scalar fields.

By the end of this task, you should have three generators for synthetic scalar fields that produce scalar fields of a given resolution and a specific number of critical points, as well as a corresponding Python script that verifies that the resulting merge tree has the expected structure.

Use this script to validate your implementation of the merge tree computation and compare your results against a reference implementation, for example the one provided by the TTK library.

You should also be able to produce a plot or table that relates input resolution, number of critical points, and runtime, and use it to discuss how the computational cost of merge tree construction depends on both the size of the scalar field and the complexity of its topology. Create plots that allow you to understand these relationships visually, for example using matplotlib.

### Hints

- Focus on 2D scalar fields for this task, as they are easier to visualize and understand. You can use a simple grid domain and define the scalar values at each vertex based on a mathematical function or a combination of functions.

## Task 3: Implement the merging step to compute the contour tree

As a next step, we want to combine the two merge trees (join tree and split tree) of a scalar field to compute the contour tree. This is the second step of the algorithm by Carr et al. and is based on a merging process that identifies corresponding nodes in the join and split trees and combines them into a single contour tree.
Implement a VTK filter (`vtkVISContourTree`) that takes the join tree and split tree as input and produces the contour tree as output.

By the end of this task, you should have a reusable VTK filter that can be called from Python, inserted into a standard VTK pipeline, and used to compute contour trees from the merge trees computed in Task 1.

### Hints

- Treat this as the second stage of the algorithm by Carr et al., not as a completely separate topology computation. The contour tree should be built from the join and split trees you already computed in Task 1.

- Keep an explicit correspondence between nodes of the join tree, nodes of the split tree, and the critical points of the input scalar field. Matching these objects robustly is often the most important practical step.

- Start with the smallest examples from Task 2 and trace the merging process by hand before implementing it. This makes it much easier to understand what should happen at leaves and how the tree is reduced step by step.

- Keep the output format close to the one used for merge trees, for example vtkGraph, so that later comparison, layout, and visualization tasks can reuse the same infrastructure.

## Task 4: Contour tree vs merge tree examples

Visualizing contour trees is even more challenging than visualizing merge trees, as they are more complex and have a more intricate structure.
Again, we first focus on understanding the structure of the resulting tree and validating on datasets with known structure before moving to layout and visualization.

First, verify that your contour tree computation produces trivial contour trees on the trivial scalar field defined in Task 2.

Next, define a more complex scalar field that produces a non-trivial contour tree, for example with multiple minima, maxima, and saddles, and verify that the resulting contour tree has the expected structure.
In particular, it is possible to design scalar fields that have the same join and split tree, but different contour trees.
Create two scalar fields with that property and verify that your implementation produces the expected contour trees for both cases.

Lastly, verify that your implementation produces a contour tree of maximum size for the scalar field defined in Task 2.
In particular, check that the resulting contour tree has at least as many nodes and arcs as the merge tree.

Again, compare the results to reference implementations provided in TTK or VTK.

### Hints

- Reuse the synthetic datasets from Task 2 as much as possible. In particular, begin with 2D examples whose critical points and level-set behavior can be inspected visually.

- When comparing merge trees and contour trees, focus first on their structure rather than on their drawing. Node identities, arc connections, and scalar ordering are usually more informative than a generic graph layout.

- To build two fields with the same join and split tree but different contour trees, think about how level sets connect between critical points, not only about how sublevel and superlevel components merge separately.

- Compare your results against a reference implementation early. Even if the visual layout differs, agreement in the critical points and arc structure is already a strong validation signal.

## Task 5: Layout

As the next step, we go beyond structural verification and use the merge and contour trees for actual visualizations of scalar fields.
Towards this, we implement distinct layout methods for the two types of tree structures.
For example, when using `vtkGraph` as the output format, this can be done by implementing a custom `vtkGraphLayoutStrategy`.

In particular, implement a layout strategy to display merge trees and contour trees clearly in the plane. The goal of this task is to move beyond computing these structures as abstract graphs and to study how layout choices affect their readability and usefulness for visualization. In particular, the drawing should make the scalar structure of the tree easy to understand and should support later interaction tasks.

Set up a visualization pipeline that displays the tree in 2D. Start with a simple baseline layout, for example by using a generic graph layout, and then design a more suitable layout for merge trees and contour trees. In particular, the layout should reflect the scalar nature of the data: critical points should be placed in a meaningful order, and the resulting drawing should make it easy to follow how components appear, merge, split, and disappear.

By the end of this task, you should have a layout method that can be applied to the trees computed in the previous tasks and that produces readable drawings for a range of datasets. Use this to compare at least two layout strategies: a generic graph or tree layout
and your own layout adapted to merge trees / contour trees.

Discuss which visual properties make the resulting drawing easy or difficult to interpret. In particular, explain how your layout helps a user understand the relationship between the tree structure and the scalar values represented by the data.

### Hints

- Treat this as a visualization task built on top of your tree computation, not as a separate graph-drawing problem. The layout should expose the structure already computed in Tasks 1 to 4 rather than replace it.

- A good first design choice is to use one axis, typically the vertical axis, to reflect the scalar value of each critical point. This often makes the drawing much easier to interpret than a fully generic graph layout.

- Think carefully about the horizontal placement of nodes and arcs. The goal is not only to avoid overlaps, but also to separate branches in a way that makes the hierarchy of the tree visually clear. Candidate criteria include edge crossings, edge bends, overlap between labels or nodes, the separation of nearby branches, and whether the scalar ordering of the nodes remains visually obvious.

- Merge trees and contour trees are not arbitrary graphs. Their drawings should help a viewer read topological events from bottom to top or top to bottom. A layout that ignores this may be formally valid but visually uninformative. The point of the task is not only to draw a tree that “looks nice,” but to understand which layout choices best communicate the topology of the scalar field.

- Compare your custom layout against a generic baseline. This comparison is useful not because the baseline is expected to be good, but because it helps make clear which visual requirements are specific to scalar topology trees.

- Use small synthetic examples first. They make it easier to debug the layout and to understand whether the drawing behaves as intended before testing it on more complex trees.

---

## Then, choose either 6a and 7a, or, 6b and 7b (or both options if you have time)

---

## Task 6a: Linked Visualization

Implement a linked visualization between your merge tree / contour tree representation and the input scalar field. The goal of this task is to move beyond computing the tree as an abstract topological object and to study how it can support actual data exploration. In particular, the visualization should help a user understand how structures in the tree correspond to structures in the spatial domain.

Set up a visualization with two coordinated views: one view showing the merge tree or contour tree, the other view showing the input scalar field in the domain. A selection made in one view should be reflected in the other. For example, selecting an arc of the tree should highlight the corresponding region in the scalar field, and selecting a point or region in the domain should make it possible to identify the corresponding location in the tree.

Extend this visualization by adding an interactive isovalue together with the corresponding contour or isosurface. The contour or isosurface should be displayed in the data view, while the same isovalue should also be represented in the tree view in a meaningful way, for example by highlighting the tree arcs intersected by that level. The goal is to turn the contour tree into an actual navigation aid for scalar-field exploration rather than just a computed output.

By the end of this task, you should have a small interactive exploration system in which the tree, the scalar field, and the current isovalue are visually linked. In particular, explain what additional insight is gained from the linked tree view and in which situations this representation is more useful than showing the scalar field alone.

### Hints

- Treat this as a visualization task built on top of your previous computation tasks, not as a separate implementation of merge trees or contour trees. The goal is to expose the information you already compute in a form that supports interactive understanding.

- For linking selections between views, `vtkAnnotationLink` is worth considering. Its purpose is precisely to let multiple views share annotation and selection information.

- For the contour or isosurface display, `vtkContourFilter` is a reasonable baseline component. On 3D data it produces isosurfaces, and on 2D data it produces isolines.

## Task 7a: Example for occluded isosurfaces

Contour trees and merge trees can be used to easily gain insights into the data that are otherwise hard to derive when only using classical rendering methods.
For example, structures that are occluded when using volume rendering or isosurfaces can be detected more easily in the abstract representation.

To showcase this, define at least one dataset where the tree helps reveal structures that are difficult to understand from the data view alone.
Demonstrate these imporvements using the linked views from the previous task.

### Hints

- The point of the task is to reflect on what kind of topological information becomes easier to see in abstract visualizations such as the contour tree. Which relationships are obvious in the tree but difficult to recognize directly in the scalar field?

---

## Task 6b: Implement topological simplification

Scalar fields that exhibit strong noise can often produce abstractions with high visual and structural complexity.
In Task 2, we have already seen synthetic datasets with merge trees as large as the original data.
To use topological abstraction in an effective way, simplification is an established procedure that separates noise from actual features of the data.

Implement a new VTK filter (`vtkVISTopologicalSimplification`) that takes as input the original scalar field together with its associated merge tree or contour tree and outputs a simplified scalar field. The corresponding simplified tree can then be recomputed or updated from this result. The goal of this task is to move beyond computing the full tree and to study how less relevant features can be removed in a controlled way in order to obtain a simpler representation of both the topology and the underlying data.

A natural starting point is to use persistence as an importance measure. Low-persistence features often correspond to small-scale fluctuations or noise, while high-persistence features tend to capture the dominant structure of the data. Your task is therefore to identify simplifiable branches or pairs of critical points in the tree, remove them according to a user-controlled threshold, and use this information to produce a simplified version of the scalar field. For this, take inspiration of seminal papers such as [Generalized Topological Simplification of Scalar Fields on Surfaces](https://dl.acm.org/doi/10.1109/TVCG.2012.228) or [Persistence-sensitive Simplification Functions on 2-manifolds](https://dl.acm.org/doi/10.1145/1137856.1137878).

Set up a comparison pipeline that allows you to inspect the original and simplified trees side-by-side, together with the corresponding original and simplified scalar data. The point is not only to reduce the number of nodes and arcs, but to understand which features are removed in the tree and how this changes the structures visible in the data.

By the end of this task, you should have a simplification method that can be applied to the trees computed in the previous tasks and that exposes a parameter controlling the degree of simplification. Use this to study how both the tree and the scalar field change as the simplification threshold increases. In particular, explain whether the simplified representation still captures the structures that would be considered important by a user, and discuss in which cases simplification improves readability and in which cases it removes relevant information.

### Hints

- Treat simplification as an extension of your existing tree pipeline, not as a separate implementation. It should remain possible to compute the full tree first and then apply simplification in a controlled and reversible way.

- Persistence is a natural importance measure, but it is not the only possible one. Even if you start with persistence, think carefully about what exactly it means for a feature to be important in the context of your data.

- Keep the simplification parameter explicit in the interface. It should be easy to compare several thresholds from Python without changing the rest of the pipeline.

- Start with small synthetic examples where the effect of simplification is easy to predict. This makes it much easier to validate whether the correct branches are removed before moving to more complex datasets.

- Compare not only the number of nodes and arcs before and after simplification, but also the visual and structural effect on the data. A simpler tree is only useful if the corresponding simplified data is easier to interpret.

## Task 7b: Evaluation: Design controlled simplification benchmarks

Design a small suite of benchmark datasets to study the effect of topological simplification on scalar fields and on derived visualizations. The goal of this task is to move from isolated examples to a more systematic understanding of when simplification is useful, what kinds of features it removes first, and how a good simplification threshold can be chosen.

Your benchmark suite should include several different types of examples. First, create a simple synthetic scalar field, for example based on a combination of Gaussians, for which the order in which features should disappear under simplification is known in advance or can be predicted with high confidence. This lets you verify that the simplification behaves as expected and that the chosen importance measure is reflected correctly in the resulting simplified field.

Second, use a dataset with additional small-scale noise and study whether simplification makes the dominant structures easier to perceive visually. In this case, the goal is not only to remove small topological features, but also to obtain a scalar field whose main structures are easier to identify by eye.

Third, include one or more examples where contours in 2D or isosurfaces in 3D become easier to inspect after simplification of the scalar field. The purpose here is to show that simplification can improve a derived visualization, not only reduce the size of the tree. For instance, simplification may remove many small components, thin protrusions, shallow pockets, or visually distracting structures that make contours difficult to read or isosurfaces difficult to interpret because of clutter or occlusion. Use the same contour or isovalue before and after simplification and study how the resulting geometry changes. In particular, discuss whether simplification mainly removes visually irrelevant structures or whether it also begins to alter features that are important for understanding the data.

Finally, include an example that studies how a useful simplification threshold can be chosen in practice. Design or use a visualization, summary plot, or other aid that helps decide at which point simplification removes mostly unimportant features while keeping the dominant structures of the data. Compare examples where this decision is relatively clear with others where no obvious threshold emerges, and discuss what makes threshold selection easy or difficult in each case.

### Hints

- As in the controlled evaluation tasks from earlier in the project, the benchmark is most useful when you can reason about the expected result before running the experiment. Synthetic scalar fields with known structure are therefore a good starting point.

- A combination of analytic functions such as Gaussians is often a convenient way to construct simple scalar fields with controllable features.

- For the contour or isosurface examples, compare the results at fixed contour or isovalues before and after simplification rather than only comparing the scalar fields themselves. `vtkContourFilter` is a reasonable baseline tool for this.

- If you want to make the effect of simplification easier to judge visually, use side-by-side views of the original and simplified scalar field, together with the corresponding contours or isosurfaces, rather than showing the simplified result alone.

- A useful way to visualize topological features from a 2D dataset is to use the third dimension as the scalar field using `vtkWarpScalar` for instance.
