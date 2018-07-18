from lxml import etree
from xml.dom import minidom
from Classes import *

def completeXML(appname,xml,rsdg,mv_rsdg,model):
    # fill in the XML with piece wise XML
    # fill in the knob cont Cost:
    knob_table = rsdg.knob_table
    coeff_table = rsdg.coeffTable
    knobmv_table = mv_rsdg.knob_table
    coeffmv_table = mv_rsdg.coeffTable
    visited_service = set()
    for services in xml.findall("service"):
        knobname = services.find("servicelayer").find("basicnode").find("nodename").text
        node = services.find("servicelayer").find("basicnode")
        if model=="piecewise":
            contpiece = etree.SubElement(node, "contpiece")
            # fill in the cont cost of each segment
            seglist = knob_table[knobname]
            seglist_mv = knobmv_table[knobname]
            for seg in seglist:
                segxml = etree.SubElement(contpiece, "seg")
                etree.SubElement(segxml,"min").text = str(seg.min)
                etree.SubElement(segxml, "max").text = str(seg.max)
                etree.SubElement(segxml, "costL").text = str(seg.a)
                etree.SubElement(segxml, "costC").text = str(seg.b)
            #find the corresponding mv
                for segmv in seglist_mv:
                    if segmv.min==seg.min:
                        etree.SubElement(segxml, "mvL").text = str(segmv.a)
                        etree.SubElement(segxml, "mvC").text = str(segmv.b)
                        break
        elif model=="quad" or model == "linear":
            contcost = etree.SubElement(node,"contcost")
            [o2,o1,c] = knob_table[knobname]
            etree.SubElement(contcost,"o2").text = str(o2)
            etree.SubElement(contcost, "o1").text = str(o1)
            etree.SubElement(contcost, "c").text = str(c)
            contmv = etree.SubElement(node,"contmv")
            [o2, o1, c] = knobmv_table[knobname]
            etree.SubElement(contmv, "o2").text = str(o2)
            etree.SubElement(contmv, "o1").text = str(o1)
            etree.SubElement(contmv, "c").text = str(c)

        # fill in the cont with
        if coeff_table==None or len(coeff_table)==0:
            continue
        if not knobname in coeff_table:
            continue
        for sink_coeff in coeff_table[knobname]:
            print knobname, sink_coeff
            print visited_service
            if(sink_coeff in visited_service):
                continue
            if model=="piecewise":
                contwith = etree.SubElement(node, "contpiecewith")
                #sink = etree.SubElement(contwith,"knob")
                sink = etree.SubElement(contwith,"knob")
                etree.SubElement(sink, "name").text = sink_coeff
                costa,costb,costc = coeff_table[knobname][sink_coeff].retrieveCoeffs()
                #mva, mvb, mvc = coeffmv_table[knobname][sink_coeff].retrieveABC()
                etree.SubElement(sink,"costa").text = str(costa)
                etree.SubElement(sink, "costb").text = str(costb)
                etree.SubElement(sink, "costc").text = str(costc)
                #etree.SubElement(sink, "mva").text = str(mva)
                #etree.SubElement(sink, "mvb").text = str(mvb)
                #etree.SubElement(sink, "mvc").text = str(mvc)
                etree.SubElement(sink, "mva").text = str(0.0)
                etree.SubElement(sink, "mvb").text = str(0.0)
                etree.SubElement(sink, "mvc").text = str(0.0)
            elif model=="quad":
                contwith = etree.SubElement(node,"contwith")
                sink = etree.SubElement(contwith, "knob")
                etree.SubElement(sink,"name").text = sink_coeff
                costa, costb, costc = coeff_table[knobname][sink_coeff].retrieveCoeffs()
                # mva, mvb, mvc = coeffmv_table[knobname][sink_coeff].retrieveABC()
                etree.SubElement(sink, "costa").text = str(costa)
                etree.SubElement(sink, "costb").text = str(costb)
                etree.SubElement(sink, "costc").text = str(costc)
                etree.SubElement(sink, "mva").text = str(0.0)
                etree.SubElement(sink, "mvb").text = str(0.0)
                etree.SubElement(sink, "mvc").text = str(0.0)
        visited_service.add(knobname)
    writeXML(appname, xml)

def getKnobByName(name,knobs):
    for knob in knobs:
        if knob.set_name == name:
            return knob
    return None

# generate structural hybrid RSDG
def genHybridXML(appname,and_cons,or_cons,knobs):
    print "RAPID-C / STAGE-1.2 : generating... hybrid structural RSDG xml"
    #write the root:resource
    xml = etree.Element("resource")
    #create all the service with range
    for knob in knobs:
        servicefield = etree.SubElement(xml,"service")
        etree.SubElement(servicefield,"servicename").text = knob.svc_name
        if knob.isContinuous():
            etree.SubElement(servicefield,"type").text = "C"
            layer = etree.SubElement(servicefield,"servicelayer")
            node = etree.SubElement(layer,"basicnode")
            etree.SubElement(node,"nodename").text = knob.set_name
            etree.SubElement(node,"contmin").text = str(knob.min)
            etree.SubElement(node, "contmax").text = str(knob.max)
        else: #discrete
            id = 0
            etree.SubElement(servicefield,"type").text = "D"
            for value in knob.values:
                layer = etree.SubElement(servicefield,"servicelayer")
                node = etree.SubElement(layer,"basicnode")
                etree.SubElement(node,"nodename").text = knob.set_name+"_"+str(id)
                etree.SubElement(node,"val").text = str(value)
                id+=1

    #create all and/contand and or/contor
    if not and_cons is None:
        for con in and_cons:
            source = con.source
            sink = con.sink
            source_knob = getKnobByName(source, knobs)
            sink_knob = getKnobByName(sink, knobs)
            # check if the sink is discrete
            if con.getSinkType() == "D" : # XX->D
                for value in con.sink_value:
                    #locate the XML Element
                    for service in xml.findall("service"):
                        if not service.find("servicename").text==sink_knob.svc_name:
                            continue
                        # locate the node location
                        for layer in service.findall("servicelayer"):
                            for node in layer.findall("basicnode"):
                                if not node.find("val").text==str(value):
                                    continue
                                # add the discrete dependency
                                if con.getSourceType() == "D": # source is discrete
                                    and_edge = etree.SubElement(node,"and")
                                    for value in con.source_value:
                                        id = source_knob.getID(value)
                                        etree.SubElement(and_edge,"name").text = source+"_"+str(id)
                                else: #source is continuous
                                    and_edge = etree.SubElement(node,"contand")
                                    etree.SubElement(and_edge,"name").text = source
                                    etree.SubElement(and_edge, "thenrangemin").text = str(con.source_value['min'])
                                    etree.SubElement(and_edge, "thenrangemax").text = str(con.source_value['max'])
            else: # XX->C #TODO: or is not printing
                # sink is the basicnode name
                for service in xml.findall("service"):
                    node = service.find("servicelayer").find("basicnode")
                    nodename = node.find("nodename").text
                    if not nodename == sink:
                        continue
                    if con.getSourceType() == "D": # source is discrete, D->C
                        and_edge = etree.SubElement(node,"and")
                        etree.SubElement(contand, "ifrangemin").text = str(con.sink_value['min'])
                        etree.SubElement(contand, "ifrangemax").text = str(con.sink_value['max'])
                        for value in con.source_value:
                            id = source_knob.getID(value)
                            etree.SubElement(and_edge,"name").text = source+"_"+str(id)
                    else: #source is continuous too, C->C
                        and_edge = etree.SubElement(node,"contand")
                        etree.SubElement(and_edge, "ifrangemin").text = str(con.sink_value['min'])
                        etree.SubElement(and_edge, "ifrangemax").text = str(con.sink_value['max'])
                        etree.SubElement(and_edge, "name").text = source
                        etree.SubElement(and_edge, "thenrangemin").text = str(con.source_value['min'])
                        etree.SubElement(and_edge, "thenrangemax").text = str(con.source_value['max'])

    #create all and/contand and or/contor
    if not or_cons is None:
        for con in or_cons:
            sources = con.sources
            sink = con.sink
            sink_value = con.sink_value
            sink_knob = getKnobByName(sink, knobs)
            # check if the sink is discrete
            if con.getSinkType() == "D" : # XX->D
                for value in con.sink_value:
                    #locate the XML Element
                    for service in xml.findall("service"):
                        if not service.find("servicename").text==sink_knob.svc_name:
                            continue
                        # locate the node location
                        for layer in service.findall("servicelayer"):
                            for node in layer.findall("basicnode"):
                                if not node.find("val").text==str(value):
                                    continue
                                # add the discrete dependency
                                for source_n, source_v in sources.iteritems():
                                    source_knob = getKnobByName(source_n, knobs)
                                    if isinstance(source_v, list): # source is discrete
                                        or_edge = etree.SubElement(node,"or")
                                        for value in source_v:
                                            id = source_knob.getID(value)
                                            etree.SubElement(or_edge,"name").text = source_n+"_"+str(id)
                                    else: #source is continuous
                                        or_edge = etree.SubElement(node,"contor")
                                        etree.SubElement(or_edge,"name").text = source_n
                                        etree.SubElement(or_edge, "thenrangemin").text = str(source_v['min'])
                                        etree.SubElement(or_edge, "thenrangemax").text = str(source_v['max'])
            else: # XX->C
                for service in xml.findall("service"):
                    node = service.find("servicelayer").find("basicnode")
                    nodename = node.find("nodename").text
                    if not nodename == sink:
                        continue
                    for source_n, source_v in sources.iteritems():
                        source_knob = getKnobByName(source_n, knobs)
                        if isinstance(source_v, list): #discrete
                            or_edge = etree.SubElement(node,"or")
                            etree.SubElement(or_edge, "ifrangemin").text = str(sink_value['min'])
                            etree.SubElement(or_edge, "ifrangemax").text = str(sink_value['max'])
                            for value in source_v:
                                id = source_knob.getID(value)
                                etree.SubElement(or_edge,"name").text = source_n+"_"+str(id)
                        else: #source is continuous too, C->C
                            or_edge = etree.SubElement(node,"contor")
                            etree.SubElement(or_edge, "ifrangemin").text = str(source_v['min'])
                            etree.SubElement(or_edge, "ifrangemax").text = str(source_v['max'])
                            etree.SubElement(or_edge, "name").text = source_n
                            etree.SubElement(or_edge, "thenrangemin").text = str(source_v['min'])
                            etree.SubElement(or_edge, "thenrangemax").text = str(source_v['max'])

    #create all contwithmv and contwith
    if len(knobs) > 1:
        length = len(knobs)
        knobList = list(knobs)
        for i in range(0,length-1):
            knobA = knobList[i].svc_name
            for service in xml.findall("service"):
                name = service.find("servicename").text
                if not name == knobA:
                    continue
                for j in range(i+1,length):
                    knobB = knobList[j].svc_name
                    contwith = etree.SubElement(service,"contwith")
                    etree.SubElement(contwith,"name").text = knobB
                    etree.SubElement(contwith, "costcoeff").text = "0.0"
                    etree.SubElement(contwith, "mvcoeff").text = "0.0"

    writeXML(appname,xml)
    return xml


def DEPRECATED_genxml(appname,rsdgfile,rsdgmvfile,cont,depfile):
    print "RAPID-C / STAGE-1.2 : generating... structural RSDG xml"
    rsdg_map,relationmap = readcontrsdg(rsdgfile)
    rsdgmv_map, relationmvmap = readcontrsdg(rsdgmvfile)
    and_list,or_list,range_map = readcontdep(depfile)

    #write the root:resource
    xml = etree.Element("resource")

    #create all the service with range
    for service, node in range_map.items():
        for node_name,node_range in node.items():
            servicefield = etree.SubElement(xml,"service")
            etree.SubElement(servicefield,"servicename").text = service
            layer = etree.SubElement(servicefield,"servicelayer")
            node = etree.SubElement(layer,"basicnode")
            etree.SubElement(node,"nodename").text = node_name
            etree.SubElement(node,"contmin").text = node_range[0]
            etree.SubElement(node, "contmax").text = node_range[1]

    #create all contcost
    if not rsdg_map is None:
        for service,paras in rsdg_map.items():
            for services in xml.findall("service"):
                name = services.find("servicelayer").find("basicnode").find("nodename").text
                if not name==service:
                    continue
                node = services.find("servicelayer").find("basicnode")
                contcost = etree.SubElement(node,"contcost")
                etree.SubElement(contcost,"o2").text = str(paras[0])
                etree.SubElement(contcost, "o1").text = str(paras[1])
                etree.SubElement(contcost, "c").text = str(paras[2])

    #create all contmv
    if not rsdgmv_map is None:
        for service,paras in rsdgmv_map.items():
            for services in xml.findall("service"):
                name = services.find("servicelayer").find("basicnode").find("nodename").text
                if not name==service:
                    continue
                node = services.find("servicelayer").find("basicnode")
                contmv = etree.SubElement(node,"contmv")
                etree.SubElement(contmv,"o2").text = str(paras[0])
                etree.SubElement(contmv, "o1").text = str(paras[1])
                etree.SubElement(contmv, "c").text = str(paras[2])

    #create all contwith
    if not relationmap is None:
        for sink,sourcelist in relationmap.items():
            for source,coeff in sourcelist.items():
                for services in xml.findall("service"):
                    node = services.find("servicelayer").find("basicnode")
                    nodename = node.find("nodename").text
                    if not nodename == sink:
                        continue
                    contwith = etree.SubElement(node,"contwith")
                    etree.SubElement(contwith,"name").text = source
                    etree.SubElement(contwith, "costcoeff").text = str(coeff)
                    etree.SubElement(contwith, "mvcoeff").text = "0"

    #create all contwithmv
    if not relationmvmap is None:
        for sink,sourcelist in relationmvmap.items():
            for source,coeff in sourcelist.items():
                for services in xml.findall("service"):
                    node = services.find("servicelayer").find("basicnode")
                    nodename = node.find("nodename").text
                    if not nodename == sink:
                        continue
                    for contwiths in node.findall("contwith"):
                        mvcoeff = contwiths.find("mvcoeff")

    #create all contand and contor
    for and_edge in and_list:
        for services in xml.findall("service"):
            node = services.find("servicelayer").find("basicnode")
            nodename = node.find("nodename").text
            if not nodename == and_edge.sink:
                continue
            contand = etree.SubElement(node,"contand")
            etree.SubElement(contand, "ifrangemin").text = and_edge.sinkmin
            etree.SubElement(contand, "ifrangemax").text = and_edge.sinkmax
            etree.SubElement(contand, "name").text = and_edge.source
            etree.SubElement(contand, "thenrangemin").text = and_edge.sourcemin
            etree.SubElement(contand, "thenrangemax").text = and_edge.sourcemax

    for or_edge in or_list:
        for services in xml.findall("service"):
            node = services.find("servicelayer").find("basicnode")
            nodename = node.find("nodename").text
            if not nodename == and_edge.sink:
                continue
            contand = etree.SubElement(node,"contor")
            etree.SubElement(contand, "ifrangemin").text = and_edge.sinkmin
            etree.SubElement(contand, "ifrangemax").text = and_edge.sinkmax
            etree.SubElement(contand, "name").text = and_edge.source
            etree.SubElement(contand, "thenrangemin").text = and_edge.sourcemin
            etree.SubElement(contand, "thenrangemax").text = and_edge.sourcemax
    writeXML(appname,xml)
    return xml

def writeXML(appname,xml):
    xmlfile = prettify(xml)
    name = appname+ ".xml"
    outputfile = open("./outputs/"+name, 'w')
    outputfile.write(xmlfile)
    outputfile.close()

def DEPRECATED_readcontdep(depfile):
    dep = open(depfile,'r')
    and_list = []
    or_list = []
    range_map = {}
    for line in dep:
        col = line.split()
        if len(col)==1:
            continue
        if len(col)==4:# this is a range line
            servicename = col[0]
            nodename = col[1]
            minrange = col[2]
            maxrange = col[3]
            range_map[servicename] = {}
            range_map[servicename][nodename] = [0.0] * 2
            range_map[servicename][nodename][0]=minrange
            range_map[servicename][nodename][1] = maxrange
        else:# this is a dep line
            type,sink,source,sinkmin,sinkmax,sourcemin,sourcemax = col
            if type=="and":
                and_list.append(RangeClass(sink,sinkmin,sinkmax,source,sourcemin,sourcemax))
            else:
                or_list.append(RangeClass(sink,sinkmin,sinkmax,source,sourcemin,sourcemax))
    return and_list,or_list,range_map

def readcontrsdg(rsdgfile):
    if rsdgfile=="":
        print "[WARNING] RSDG not provided, generating strucutral info only"
        return [None,None]
    rsdg = open(rsdgfile,'r')
    rsdg_map = {}
    relation_map = {}
    for line in rsdg:
        col = line.split()
        name = col[0]
        val = col[1]
        curPara = name.split("_")
        service = curPara[0]
        coeff = curPara[1]
        lvl = 0
        dependent = ""
        if coeff == "2":
            lvl = 2
        elif coeff == "1":
            lvl = 1
        elif coeff == "c":
            lvl = 0
        else:
            lvl = -1
            dependent = coeff
        if not (service in rsdg_map):
            rsdg_map[service] = [0.0] * 3
        if not (service in relation_map):
            relation_map[service] = {}
        if not lvl == -1:
            rsdg_map[service][lvl] = float(val)
        else:
            relation_map[service][dependent] = float(val)
    rsdg.close()
    return rsdg_map, relation_map


class RangeClass:
    def __init__(self, sink, sinkmin, sinkmax,source,sourcemin,sourcemax):
        self.sinkmin = sinkmin
        self.sinkmax = sinkmax
        self.sourcemin = sourcemin
        self.sourcemax = sourcemax
        self.sink = sink
        self.source = source

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = etree.tostring(elem)
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")
