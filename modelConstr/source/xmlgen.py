from lxml import etree
from xml.dom import minidom
from Classes import *

def completeXML(appname,xml,rsdg,mv_rsdg):
    # fill in the XML with piece wise XML
    # fill in the knob cont Cost:
    knob_table = rsdg.knob_table
    coeff_table = rsdg.coeffTable
    knobmv_table = mv_rsdg.knob_table
    coeffmv_table = mv_rsdg.coeffTable
    visited_service = set()
    for services in xml.findall("service"):
        knobname = services.find("servicelayer").find("basicnode").find("nodename").text
        visited_service.add(knobname)
        node = services.find("servicelayer").find("basicnode")
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
        # fill in the cont with
        if coeff_table==None or len(coeff_table)==0:
            continue
        if not knobname in coeff_table:
            continue
        for sink_coeff in coeff_table[knobname]:
            if(sink_coeff in visited_service):
                continue
            contwith = etree.SubElement(node, "contpiecewith")
            #sink = etree.SubElement(contwith,"knob")
            sink = etree.SubElement(contwith,"knob")
            etree.SubElement(sink, "name").text = sink_coeff
            costa,costb,costc = coeff_table[knobname][sink_coeff].retrieveABC()
            mva, mvb, mvc = coeffmv_table[knobname][sink_coeff].retrieveABC()
            etree.SubElement(sink,"costa").text = str(costa)
            etree.SubElement(sink, "costb").text = str(costb)
            etree.SubElement(sink, "costc").text = str(costc)
            #etree.SubElement(sink, "mva").text = str(mva)
            #etree.SubElement(sink, "mvb").text = str(mvb)
            #etree.SubElement(sink, "mvc").text = str(mvc)
            etree.SubElement(sink, "mva").text = str(mva)
            etree.SubElement(sink, "mvb").text = str(0.0)
            etree.SubElement(sink, "mvc").text = str(mvc)
    writeXML(appname, xml)

def genxml(appname,rsdgfile,rsdgmvfile,cont,depfile):
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

def readcontdep(depfile):
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