---
name: coding-robotics
description: "ROS 2 robotics middleware: nodes, topics, services, actions, lifecycle, DDS QoS, tf2 transforms, Nav2 / MoveIt 2 stacks, simulation in Gazebo / Isaac Sim. Triggers: ROS, ROS 2, robotics, rclcpp, rclpy, DDS, tf2, Nav2, MoveIt, URDF, Gazebo, Isaac Sim, robot, manipulator, AGV, AMR."
domain: coding
subdomain: robotics
facets:
  - lang:python
  - lang:cpp
  - lang:rust
  - target:linux
  - target:embedded
  - vendor:ros2
  - vendor:nvidia
applies_when:
  any_of:
    - "task writes ROS 2 nodes (rclcpp / rclpy / ros2_rust) — topics, services, actions, parameters"
    - "task tunes DDS QoS, multicast, or discovery for a real robot deployment"
    - "task wires tf2 frames, URDF / Xacro / SDF descriptions, or robot_state_publisher"
    - "task uses Nav2, MoveIt 2, or ros2_control for navigation, manipulation, or motor control"
    - "task simulates a robot in Gazebo (gz-sim) or NVIDIA Isaac Sim and validates against ROS 2 topics"
version: 0.1.0
---
# Coding / Robotics (ROS 2)

## When to use

Open this skill when the deliverable runs on a real or simulated
robot under the ROS 2 middleware contract. For pure ML perception
models *consumed* by the robot, prefer
[`../../ml/inference/SKILL.md`](../../ml/inference/SKILL.md). For
synthetic-data generation in Unity/UE, use
[`../../gameengine/synthetic-data/SKILL.md`](../../gameengine/synthetic-data/SKILL.md).
For VLM-driven scene reasoning *as a node*, compose with
[`../../ml/vlm-spatial/SKILL.md`](../../ml/vlm-spatial/SKILL.md).

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **ROS 2 graph entities** — *nodes* (processes/components),
  *topics* (pub/sub, anonymous), *services* (request/response,
  not for long-running work), *actions* (long-running, with
  goal/feedback/result), *parameters* (per-node typed config).
- **Distributions** — pick an LTS (`Humble` 2027 EOL,
  `Jazzy` 2029 EOL); avoid non-LTS in production. Distros
  define ABI; mixing breaks subtly.
- **DDS / RMW** — the wire layer underneath. Default RMWs:
  `rmw_fastrtps_cpp` (Fast DDS), `rmw_cyclonedds_cpp`
  (Cyclone DDS). Behaviour, discovery, and multicast handling
  differ — pick one and pin via `RMW_IMPLEMENTATION`.
- **QoS profiles** — `Reliability` (reliable / best-effort),
  `Durability` (volatile / transient-local),
  `History` (keep-last / keep-all + depth),
  `Deadline`, `Liveliness`, `Lifespan`. *Compatibility is
  asymmetric*: subscriber must be ≤ publisher.
- **tf2** — global transform tree. *Static* transforms (URDF
  joints rigid in robot frame) on `/tf_static`
  (transient-local QoS); *dynamic* on `/tf`. Buffer 10 s by
  default; query with `tf2_ros::Buffer::lookupTransform`.
- **Lifecycle nodes** — managed state machine
  (`unconfigured → inactive → active → finalized`); used by
  Nav2 and `ros2_control` for orderly bring-up.
- **Composition** — multiple nodes in one process via
  `rclcpp::Node` components in a container (`component_container`,
  `component_container_mt`). Removes serialisation cost on
  intra-process comms.
- **Executors** — `SingleThreadedExecutor`,
  `MultiThreadedExecutor`, `StaticSingleThreadedExecutor`. Choose
  per-node based on callback re-entrancy and real-time needs.
- **Callback groups** — `MutuallyExclusive` (default) vs
  `Reentrant`. Wrong group on a service that calls another
  service in the same node = deadlock.
- **`ros2_control`** — hardware-interface plugin layer +
  controller manager. Real-time loop runs at 100 Hz – 1 kHz
  inside a deterministic thread; ROS API exposed asynchronously.
- **Nav2** — modular navigation: planner, controller, behaviour
  tree, recovery, costmap (2D / 3D voxel). Lifecycle-managed.
- **MoveIt 2** — manipulation planning: kinematics, OMPL /
  STOMP / Pilz planners, planning scene, servo, trajectory
  execution.
- **URDF / Xacro / SDF** — URDF (rigid robot description, ROS
  ecosystem); Xacro (URDF macros); SDF (Gazebo-native,
  superset of URDF).

## Recommended patterns

1. **Pin the distro and the RMW.** Single distro per workspace;
   set `RMW_IMPLEMENTATION` and `ROS_DOMAIN_ID` in launch /
   systemd unit / Dockerfile.
2. **Author launch in Python `launch` / `launch_ros`.** Compose
   `IncludeLaunchDescription`, `LifecycleNode`, and condition
   substitutions; avoid bash glue.
3. **Use components, not standalone nodes**, for the inner perf
   loop. Same process = zero-copy intra-process pubs.
4. **Match QoS to the data.** Sensor streams: best-effort,
   keep-last 5; commands: reliable, keep-last 1; latched
   metadata (map, robot description): transient-local.
5. **Never block a callback.** Long work goes to a separate
   thread or an action server; otherwise the executor stalls
   and tf lookups fail.
6. **Drive long-running tasks with actions, not services.**
   Goals can be cancelled and emit feedback.
7. **Keep tf consistent.** One publisher per frame edge;
   `robot_state_publisher` for URDF joints; static
   transforms for sensor mounts.
8. **Parameterise via YAML + declared parameters** (with
   types and descriptors); avoid global namespaces.
9. **Simulate before bringing up real hardware.** Gazebo / Isaac
   Sim with the same launch graph; switch via launch arg.
10. **Record `mcap` bags continuously** in field deployments;
    smaller and more robust than the legacy SQLite format.
11. **Deterministic replay for tests.** `ros2 bag play` +
    `--clock`; assert on topics with `launch_testing`.

## Pitfalls (subdomain-specific)

- ❌ **Blocking inside a service callback that calls another
  service on the same node** with default callback groups:
  guaranteed deadlock. Use a `Reentrant` group or a separate
  thread.
- ❌ **Publishing tf at the wrong rate.** Down-sampling /tf
  causes tf2 to extrapolate or fail; up-sampling burns CPU and
  saturates DDS.
- ❌ **Mismatched QoS.** A reliable subscriber missing a
  best-effort publisher: silent no-data. Inspect with
  `ros2 topic info -v`.
- ❌ **Using global namespaces (`/`).** Two robots on one DDS
  domain will fight; namespace each robot
  (`__ns:=/robot1`).
- ❌ **Ignoring `use_sim_time`.** In sim with `/clock`,
  forgetting `use_sim_time:=true` breaks every timer and tf
  lookup.
- ❌ **Discovery storms.** Hundreds of nodes on one domain
  saturate the network with PDP traffic. Use Discovery Server
  or partitioned domains.
- ❌ **Mixing rclcpp components with rclpy nodes** when
  zero-copy matters; intra-process only works within a single
  language-runtime container.
- ❌ **Long-running work in lifecycle `on_activate`.** Bring-up
  hangs and Nav2 marks the node faulty.
- ❌ **Trusting `clock` from a single source in a multi-machine
  setup.** Always run `chrony` / PTP; tf extrapolation
  errors otherwise.
- ❌ **Embedding secrets / API keys in launch YAML.** Use
  parameters loaded from a secret store at start-up.
- ❌ **Building everything in one `colcon` package.** Slow
  rebuilds; split by responsibility (`*_msgs`, `*_bringup`,
  `*_description`, `*_control`).

Domain-wide pitfalls live in [`../_shared/pitfalls.md`](../_shared/pitfalls.md).

## Procedure

1. **Define the message contract.** Custom `*.msg` / `*.srv` /
   `*.action` in a dedicated `*_msgs` package; freeze before
   wiring nodes.
2. **Author the URDF / Xacro** for the robot; validate with
   `check_urdf` and `urdf_to_graphiz`.
3. **Stand up `robot_state_publisher` + a fake controller** in
   sim; verify tf tree and Rviz visualisation.
4. **Implement the perception/control nodes** as components,
   with declared parameters and lifecycle if part of Nav2 /
   MoveIt 2.
5. **Configure QoS per topic.** Document each public topic's
   profile in the package README.
6. **Wire bring-up via Python launch.** Composition container,
   parameters from YAML, conditional `use_sim_time`.
7. **Add Nav2 / MoveIt 2 stacks** if applicable; tune costmaps
   / planners on simulation traces before hardware.
8. **Profile.** `ros2 topic hz`, `ros2 topic bw`,
   `ros2_tracing` / `tracetools` for callback latency, perf
   record for inner loops.
9. **Field-replay.** Record `mcap` bags during runs; replay
   under regression tests.
10. **Harden.** Watchdogs, e-stop integration, lifecycle
    fault transitions, network partition handling.

## Validation

After completing the procedure, run:

```sh
# Static checks
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
ament_cpplint && ament_cppcheck && ament_uncrustify
ament_flake8 && ament_pep257                   # Python nodes

# Runtime introspection
ros2 doctor --report
ros2 topic list -t                              # types must match contract
ros2 topic hz /scan                             # rate sanity
ros2 topic info -v /cmd_vel                     # QoS endpoints

# Integration
colcon test --event-handlers console_direct+
launch_test test/integration.launch_test.py     # gtest + launch_testing
ros2 bag play --clock recorded.mcap \
    && ros2 launch my_pkg integration.launch.py use_sim_time:=true
```

## See also

- [`../../ml/inference/SKILL.md`](../../ml/inference/SKILL.md) —
  for perception models served as ROS 2 nodes.
- [`../../ml/edge-inference/SKILL.md`](../../ml/edge-inference/SKILL.md)
  — when those models run on the robot's on-board accelerator.
- [`../../gameengine/synthetic-data/SKILL.md`](../../gameengine/synthetic-data/SKILL.md)
  — for synthetic training data sourced from Isaac Sim / UE.
- [`../embedded/SKILL.md`](../embedded/SKILL.md) — for the
  micro-ROS firmware side talking to ROS 2 over serial / UDP.
- ROS 2 documentation — <https://docs.ros.org/en/rolling/>
- DDS QoS reference — <https://docs.ros.org/en/rolling/Concepts/Intermediate/About-Quality-of-Service-Settings.html>
- Nav2 — <https://docs.nav2.org/>
- MoveIt 2 — <https://moveit.picknik.ai/>
- NVIDIA Isaac Sim — <https://docs.omniverse.nvidia.com/isaacsim/>
