from gensie.baseline import OfficialParticipant
from gensie.baseline import SyntheticAnchorAgent

participant = OfficialParticipant()
info = participant.get_info()

pipeline_names = [p.name for p in info.pipelines]
print(f"Pipelines in info: {pipeline_names}")

if "synthetic-anchor" in participant.pipelines:
    print("synthetic-anchor is registered in participant.pipelines")
    agent = participant.get_agent("synthetic-anchor")
    if isinstance(agent, SyntheticAnchorAgent):
        print("synthetic-anchor agent is of type SyntheticAnchorAgent")
    else:
        print(f"synthetic-anchor agent is of type {type(agent)}")
else:
    print("synthetic-anchor is NOT registered in participant.pipelines")

if "synthetic-anchor" in pipeline_names:
    print("synthetic-anchor is in get_info().pipelines")
    p_info = next(p for p in info.pipelines if p.name == "synthetic-anchor")
    print(f"Description: {p_info.description}")
