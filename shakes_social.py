from xml.dom.minidom import parse, parseString
from collections import Counter
import pydot
import networkx as nx
import matplotlib.pyplot as plt
import glob
from math import log, sqrt

def analyze(play,num_overlap):

    dom = parse(play)

    speaker_count = Counter()

    for node in dom.getElementsByTagName('SPEECH'):
        num_lines = len(node.getElementsByTagName('LINE'))
        for speakers in node.getElementsByTagName('SPEAKER'):
            if speakers.firstChild:
                speaker_count.update({speakers.firstChild.nodeValue.upper(): num_lines})

    actors_scene = {}

    for act in dom.getElementsByTagName('ACT'):
        act_name = act.getElementsByTagName('TITLE')[0].firstChild.nodeValue
        for scene in act.getElementsByTagName('SCENE'):
            scene_name = scene.getElementsByTagName('TITLE')[0].firstChild.nodeValue
            scene_id = act_name + ' ' + scene_name.split('.')[0]

            speaker_list = []
            for speaker in scene.getElementsByTagName('SPEAKER'):
                if speaker.firstChild:
                    speaker_list.append(str(speaker.firstChild.nodeValue).upper())
                    actors_scene[str(scene_id)] = set(speaker_list)

    graph = pydot.Dot(graph_type='graph',overlap=False)

    N = 100
    for speaker in speaker_count:
        width = log(2*float(speaker_count[speaker]))/float(1)
        #print width
        if speaker in [s for s, l in speaker_count.most_common(N)]:
            fontsize = 1.2*(width*72/(len(speaker)))
            node = pydot.Node(
                speaker,
                fixedsize=True,
                fontsize=fontsize,
                shape='circle',
                width=width,
                penwidth=10
            )
        else:
            node = pydot.Node(
                speaker,
                fixedsize=True,
                shape='point',
                width=width,
                penwidth=3
            )

        graph.add_node(node)

    edge_list = {}
    for scene in actors_scene:
        chars = sorted(actors_scene[scene]) #needs to be sorted, I assume in one order
        num_char = len(chars)
        for i in range(num_char):
            for j in range(i+1,num_char):
                if not edge_list.has_key(chars[i] + ' ' + chars[j]):
                    edge_list[chars[i] + ' ' + chars[j]] = pydot.Edge(
                        chars[i],
                        chars[j],
                        weight=1,
                        penwidth=3
                        )
                else:
                    edge_list[chars[i] + ' ' + chars[j]].set_weight(
                        edge_list[chars[i] + ' ' + chars[j]].get_weight()+1
                        )
                    edge_list[chars[i] + ' ' + chars[j]].set_penwidth(
                        edge_list[chars[i] + ' ' + chars[j]].get_penwidth()+5
                        )

    for edge in edge_list:
        if edge_list[edge].get_weight()>=num_overlap:
            graph.add_edge(edge_list[edge])

    keep_nodes = []
    for edge in graph.get_edge_list():
        keep_nodes.append(edge.get_source())
        keep_nodes.append(edge.get_destination())

    for node in graph.get_node_list():
        if not str(node.get_name()) in keep_nodes:
            graph.del_node(node)
            
    name = play.split('.')[0]
    print name
    
    graph.write_png(name + '_' + str(num_overlap) +'.png',prog='neato')

for overlap in range(1,6):
    for play in glob.glob('Tragedies/r_and_j.xml'):
        analyze(play,overlap)
