#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xml.etree import ElementTree
from typing import List, Dict, Any


def xmlToTreeDict(xml_tree: ElementTree.Element) -> Dict[str, Any]:
   def __treeSearch(output: Dict[str, Any], root: ElementTree.Element):
       for child in root:
           child_name = child.tag + "#" + child.attrib["name"] if "name" in child.attrib else child.tag
           attributes = {"@" + key: value for key, value in child.attrib.items()}
           if len(child) > 0:
               if child.text.strip(): attributes["text"] = child.text.strip()
               output[child_name] = __treeSearch(attributes, child)
           else:
               output[child_name] = attributes
               output[child_name]["text"] = child.text.strip() if child.text else ""
       return output
   tree_dict = __treeSearch({"@" + key: value for key, value in xml_tree.attrib.items()}, xml_tree)
   return { xml_tree.tag: tree_dict }


def treeDictToXml(tree_dict: Dict[str, Any]) -> ElementTree.Element:
    def __treeSearch(output: ElementTree.Element, root: Dict[str, Any]):
        for key, value in root.items():
            if "@" in key:
                output.set(key.split("@")[1], value)
            elif "text" == key:
                output.text = value
            else:
                child_name = key.split("#")[0]
                node = ElementTree.SubElement(output, child_name)
                __treeSearch(node, value)
        return output
    xml_root = __treeSearch(ElementTree.Element(next(iter(tree_dict))), tree_dict[next(iter(tree_dict))])
    return xml_root


def treeDictSearch(tree_dict: Dict[str, Any], target_key: str) -> Any:
    def __treeSearch(output: Dict[str, Any], tree: Dict[str, Any], target: str):
        for key, value in tree.items():
            if key == target:
                output = value
            elif type(value).__name__ == "dict":
                output = __treeSearch(output, value, target)
            else:
                pass
        return output
    tree_target = __treeSearch(None, tree_dict, target_key)
    return tree_target
