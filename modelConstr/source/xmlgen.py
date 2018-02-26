from lxml import etree
from xml.dom import minidom

def genxml(rsdgfile,cont,depfile):
    rsdg_map,relationmap = readcontrsdg(rsdgfile)
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
            etree.SubElement(node,"contmax").text = node_range[0]
            etree.SubElement(node, "contmin").text = node_range[1]

    #create all contcost
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

    #create all contwith
    print relationmap
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

    #write to xml
    #xmlfile = etree.ElementTree(prettify(xml))
    xmlfile = prettify(xml)
    outputfile = open("xml.xml",'w')
    outputfile.write(xmlfile)
    outputfile.close()
    #xmlfile.write("xml.xml")

def readcontdep(depfile):
    dep = open(depfile,'r')
    and_list = []
    or_list = []
    range_map = {}
    for line in dep:
        col = line.split()
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