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

aliases and the actual name must be globally unique

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

## conventions

everything should be meaningful in the syntax, including aliases
and example to illustrait this would be
```
# bad example

colonial system (col_sys) : Methods for governing conquered territories

col_sys < (direct) Direct rule: European officials replace local elites
col_sys < (indirect) Indirect rule: Rule through local collaborators
col_sys < (assim) Assimilation: Transform into Western model
col_sys < (assoc) Association: Preserve local traditions
```

```
# good example

colonial system (col_sys) : Methods for governing conquered territories

col_sys < (methods of rulerish) 1. Direct rule: European officials replace local elites\n2. Indirect rule: Rule through local collaborators\n
col_sys < (assimilation) Transform into Western model
col_sys < (association) Preserve local traditions
```

comparing the bad example to the good example. the good example was able to use the 'aliases' as effective labels, as questions. the bad example had aliases which couldn't be used to extend the functionaly of the notes.
