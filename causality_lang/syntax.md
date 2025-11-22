# features
  - define
    - vocab
    - keywords / alias
  - elaboration
  - logical connects
    - caused
    - contributed
    - influenced
    - etc
  - non priorities
    - math equations
    - 推导
    - stuff

# specifics

## node types

ancestor nodes: vocabs basically
sub nodes: child nodes

## define

defining nodes in the info tree

\[**vocab**] (**alias**) : \[...]
protestant reformation (protref) : some event in Europe

refer to definition via ||

... (): ... |vocab word|

## elaborations

defining sub nodes which is a child (it points to) another node

\[**parent node**] < (**sub-alias**) \[...]
protref < (prots) there were protestants involved in this
protref.prots < the protestants were protestants

## logical connections

\[**node a**] <**connection type**> \[**node b**] & \[**node c**] & ...

protref <caused> religious diversity & ...

caused
contributed
influenced
contemporary

## extended syntax

\# for annotations

protestant reformation (protref) : some event in Europe
< (prots) there were protestants involved in this
<< the protestants were protestants

# actual implementation

per-line

if : present
  definition
elif <> present
  connection
elif < present
  subnode
