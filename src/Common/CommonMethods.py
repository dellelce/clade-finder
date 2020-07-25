# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 13:19:15 2019

@author: hunte
"""

import tabix


def encodeTabix(snp):
    return snp.replace("(", "_L_PAREN_").replace(")", "_R_PAREN_").replace(
        "+", "_PLUS_").replace("-",
                               "_MINUS_").replace(" ",
                                                  "").replace(".", "_DOT_")


def decodeTabix(snp):
    return snp.replace("_L_PAREN_", "(").replace("_R_PAREN_", ")").replace(
        "_PLUS_", "+").replace("_MINUS_", "-").replace("_DOT_", ".")


def getEncodedPositivesNegatives(snps):
    positives = set([])
    negatives = set([])
    for snp in snps:
        stripped = snp.strip()
        if stripped != "":
            if stripped[-1] == "+":
                thepos = stripped[0:-1]
                encoded = encodeTabix(thepos)
                positives.add(encoded)
            else:
                if stripped[-1] == "-":
                    theneg = stripped[0:-1]
                    encoded = encodeTabix(theneg)
                    negatives.add(encoded)
    return positives, negatives


def getProductTabix(snp, tb):
    try:
        productResults = tb.querys(snp + ":3-3")
        for snp in productResults:
            return snp[3]
    except:
        return None


def getPositionSNP(position, allele, tb):
    try:
        positionResults = tb.querys(position + ":1-1")
        snps = []
        for snp in positionResults:
            if snp[4] == allele:
                snps.append(snp[3] + "+")
            else:
                snps.append(snp[3] + "-")
        return snps
    except:
        return None


def getSNPsFrom23AndMe(twentyThreeAndMeFile, tbPositionSNPsFile):
    positives = []
    tbPositionSNPs = tabix.open(tbPositionSNPsFile)

    with open(twentyThreeAndMeFile, "r") as r:
        lines = r.readlines()
        xTotal = 0
        yTotal = 0
        for line in lines:
            chomped = line.replace("\n", "")
            splt = chomped.split("\t")
            if len(splt) == 4:
                if splt[1] == "Y":
                    position = splt[2]
                    if len(splt[3]) > 0:
                        allele = splt[3][0]
                        if allele != "-":
                            yTotal = yTotal + 1
                            posSNPs = getPositionSNP(position, allele,
                                                     tbPositionSNPs)
                            if posSNPs:
                                for posSNP in posSNPs:
                                    if posSNP != "S47+":
                                        positives.append(posSNP)
                else:
                    if splt[1] == "X":
                        if len(splt[3]) > 0:
                            allele = splt[3][0]
                            if allele != "-":
                                xTotal = xTotal + 1
            else:
                if len(splt) == 5:
                    if splt[1] == "24":
                        position = splt[2]
                        allele = splt[3]
                        if allele != "0" and allele != "":
                            yTotal = yTotal + 1
                            posSNPs = getPositionSNP(position, allele,
                                                     tbPositionSNPs)
                            if posSNPs:
                                for posSNP in posSNPs:
                                    positives.append(posSNP)
                    else:
                        if splt[1] == "25":
                            allele = splt[3]
                            if allele != "0" and allele != "":
                                xTotal = xTotal + 1
                else:
                    if len(splt) == 1:
                        splt = chomped.replace("\"", "").split(",")
                        if len(splt) == 4:
                            if splt[1] == "Y":
                                position = splt[2]
                                if len(splt[3]) > 0:
                                    allele = splt[3][0]
                                    if allele != "-":
                                        yTotal = yTotal + 1
                                        posSNPs = getPositionSNP(
                                            position, allele, tbPositionSNPs)
                                        if posSNPs:
                                            for posSNP in posSNPs:
                                                positives.append(posSNP)
                            else:
                                if splt[1] == "X":
                                    if len(splt[3]) > 0:
                                        allele = splt[3][0]
                                        if allele != "-":
                                            xTotal = xTotal + 1
    r.close()
    xReads = xTotal
    yReads = yTotal
    return positives, xReads, yReads


def getCladeSNPs(clade, tb):
    try:
        claderesults = tb.querys(clade + ":1-1")
        snps = []
        for snp in claderesults:
            snps.append(snp[3])
        return snps
    except:
        print(clade, " has no SNPs")
        return []


def getSNPClades(snp, tb):
    try:
        SNPresults = tb.querys(snp + ":1-1")
        clades = []
        for clade in SNPresults:
            clades.append(clade[3])
        return clades
    except:
        return []


def getParentTabix(clade, tb):
    try:
        parentResults = tb.querys(clade + ":2-2")
        parent = None
        for parentResult in parentResults:
            parent = parentResult[3]
        if parent == '':
            return "Adam"
        return parent
    except:
        return None


def getChildrenTabix(clade, tb):
    try:
        childResults = tb.querys(clade + ":3-3")
        children = []
        for childResult in childResults:
            child = childResult[3]
            children.append(child)
        return children
    except:
        return []


def getUniqueSNPTabix(snp, tb):
    returnvalue = snp
    try:
        uniqueSNPResults = tb.querys(snp + ":2-2")
        for uniqueSNPResult in uniqueSNPResults:
            if uniqueSNPResult is not None and len(
                    uniqueSNPResult) > 3 and uniqueSNPResult[3] is not None:
                returnvalue = uniqueSNPResult[3]
    finally:
        return returnvalue


def getUniqueSNPsetTabix(snps, tb):
    uniqueSNPs = set([])
    for snp in snps:
        uniqueSNPs.add(getUniqueSNPTabix(snp, tb))
    return uniqueSNPs


def recurseToRootAddParents(clade, hier, tb):
    parent = getParentTabix(clade, tb)
    if parent != None:
        hier[clade] = parent
        if parent not in hier:
            recurseToRootAddParents(parent, hier, tb)


def createChildMap(hier):
    childMap = {}
    for child in hier:
        if hier[child] not in childMap:
            childMap[hier[child]] = [child]
        else:
            childMap[hier[child]].append(child)
    return childMap


def createMinimalTree(positives, tbSNPclades, tbCladeSNPs):
    clades = set([])
    for snp in positives:
        for clade in getSNPClades(snp, tbSNPclades):
            clades.add(clade)
    hier = {}
    for clade in clades:
        recurseToRootAddParents(clade, hier, tbCladeSNPs)
    return hier, clades


def createMiminalTreePanelRoots(panelRoots, tbCladeSNPs):
    hier = {}
    for clade in panelRoots:
        recurseToRootAddParents(clade, hier, tbCladeSNPs)
    return hier


def createCladeSNPs(hierarchy, tb):
    cladeSNPs = {}
    for clade in hierarchy:
        if hierarchy[clade] not in hierarchy:
            cladeSNPs[hierarchy[clade]] = getCladeSNPs(hierarchy[clade], tb)
        cladeSNPs[clade] = getCladeSNPs(clade, tb)
    return cladeSNPs


def getTotalSequence(clade, hierarchy):
    sequence = [clade]
    thisClade = clade
    while thisClade in hierarchy:
        thisClade = hierarchy[thisClade]
        sequence.append(thisClade)
    return sequence[:-1]


def getScore(sequence, totalSequence):
    return float(len(sequence)) / len(totalSequence)


def printSolutions(solutions):
    for solution in solutions:
        print(" ".join(solution), getScore(solution))


def getConflicts(sequence, negatives, cladeSNPs):
    conflictingNegatives = []
    for hg in sequence:
        if any(snp in negatives for snp in cladeSNPs[hg]):
            conflictingNegativeSnps = ""
            for snp in cladeSNPs[hg]:
                if snp in negatives:
                    conflictingNegativeSnps += " " + snp
            conflictingNegatives.append(hg + " @" + conflictingNegativeSnps +
                                        ";")
    return conflictingNegatives


import numpy as np


def getPathScores(fullSequence, confirmed, negatives, positives, conflicts,
                  cladeSNPs):
    scores = []
    last = fullSequence[-1]
    weights = 0
    for thing in fullSequence:
        weight = len(cladeSNPs[thing])
        if thing in confirmed:
            negs = len(negatives.intersection(set(cladeSNPs[thing])))
            poses = len(positives.intersection(set(cladeSNPs[thing])))
            if last == thing:
                scores.append(1.0 * weight)
                weights += weight
            else:
                scores.append(
                    weight * (-1.0 + 2.0 * float(poses) / float(poses + negs)))
                weights += weight
        else:
            if thing in conflicts:
                negs = len(negatives.intersection(set(cladeSNPs[thing])))
                scores.append(weight * -1 * negs)
                weights += weight
    return np.divide(scores, weights)


def getPathScoresSimple(fullSequence, negatives, positives, cladeSNPs):
    scores = []
    for thing in fullSequence[:-1]:
        thescore = len(positives.intersection(set(cladeSNPs[thing]))) - len(
            negatives.intersection(set(cladeSNPs[thing])))
        scores.append(thescore)
    scores.append(len(positives.intersection(set(
        cladeSNPs[fullSequence[-1]]))))
    return scores


def isBasal(clade, negatives, positives, hierarchy, childMap, cladeSNPs):
    basal = False
    children = getChildren(clade, childMap)
    if len(children) > 0:
        basal = True
        for child in children:
            isNeg = len(negatives.intersection(set(cladeSNPs[child]))) > 0
            isPos = len(positives.intersection(set(cladeSNPs[child]))) > 0
            if isNeg and not isPos:
                basal = basal and True
    return basal


def getWarningsConf(conflicts):
    messages = []
    for conflict in conflicts:
        messages.append(" " + conflict)
    return messages


from operator import itemgetter


def getRankedSolutionsSimple(pos_clades, positives, negatives, hierarchy,
                             childMap, cladeSNPs):
    scoredSolutions = []
    for clade in pos_clades:
        totalSequence = getTotalSequence(clade, hierarchy)
        totalSequence.reverse()
        conflicts = getConflicts(totalSequence, negatives, cladeSNPs)
        scores = getPathScoresSimple(totalSequence, negatives, positives,
                                     cladeSNPs)
        scoredSolutions.append([
            totalSequence, clade,
            np.average(scores),
            np.sum(scores),
            float(np.sum(scores)),
            getWarningsConf(conflicts)
        ])

    scoredSolutions = sorted(scoredSolutions, key=itemgetter(4), reverse=True)

    return scoredSolutions


def getRankedSolutions(positives, negatives, hierarchy, childMap, cladeSNPs):
    solutions = []
    recurseDownTree(positives, hierarchy, childMap, cladeSNPs, solutions)
    scoredSolutions = []
    print(solutions)
    uniqueSolutions = removeDuplicates(solutions)
    print(uniqueSolutions)
    for solution in solutions:
        lastChainMoreNegThanPos = True
        removed = 0
        while lastChainMoreNegThanPos and removed < len(solution):
            totalSequence = getTotalSequence(solution[-1 - removed], hierarchy)
            totalSequence.reverse()
            conflicts = getConflicts(totalSequence, negatives, cladeSNPs)
            scores = getPathScores(totalSequence, solution, negatives,
                                   positives, conflicts, cladeSNPs)
            clade = solution[-1 - removed]
            if isBasal(clade, negatives, positives, hierarchy, childMap,
                       cladeSNPs):
                clade = clade + "*"
            scoredSolutions.append([
                totalSequence, clade,
                np.average(scores),
                np.sum(scores),
                getPositive(scores) * np.sum(scores),
                getWarningsConf(conflicts)
            ])

            removed = removed + 1
            if scores[-1] > 0.5:
                lastChainMoreNegThanPos = False
            #else:
            #print(totalSequence, scores[-1], scores)

        #print(scoredSolutions[-1])
    scoredSolutions = sorted(scoredSolutions, key=itemgetter(4), reverse=True)

    return scoredSolutions


def getPositive(scores):
    totscore = 0
    for score in scores:
        if score > 0:
            totscore += 1
    return totscore


def removeDuplicates(arr):

    n = len(arr)
    # Return, if array is
    # empty or contains
    # a single element
    if n == 0 or n == 1:
        return n

    temp = list(range(n))

    # Start traversing elements
    j = 0
    for i in range(0, n - 1):

        # If current element is
        # not equal to next
        # element then store that
        # current element
        if arr[i] != arr[i + 1]:
            temp[j] = arr[i]
            j += 1

    # Store the last element
    # as whether it is unique
    # or repeated, it hasn't
    # stored previously
    temp[j] = arr[n - 1]
    j += 1

    # Modify original array
    for i in range(0, j):
        arr[i] = temp[i]

    return arr


def getChildren(clade, childMap):
    #    children = []
    #    for child in childParents:
    #        if childParents[child] == clade:
    #            children.append(child)
    #
    if clade in childMap:
        return childMap[clade]
    else:
        return []


def isInChildrenThisLevel(clade, positives, childMap, cladeSNPs):
    children = getChildren(clade, childMap)
    inChildren = []
    for child in children:
        if any(snp in positives for snp in cladeSNPs[child]):
            inChildren.append(child)
    return inChildren


def recurseDownTreeUntilFirstHits(clade, positives, childParents, childMap,
                                  cladeSNPs):
    posChildrenThisLevel = isInChildrenThisLevel(clade, positives, childMap,
                                                 cladeSNPs)
    for child in getChildren(clade, childMap):
        if child not in posChildrenThisLevel:
            childResult = recurseDownTreeUntilFirstHits(
                child, positives, childParents, childMap, cladeSNPs)
            for cres in childResult:
                posChildrenThisLevel.append(cres)
    return posChildrenThisLevel


def refineHitsRecursively(sequences, positives, childParents, childMap,
                          cladeSNPs, solutions):
    for sequence in sequences:
        refinedResults = recurseDownTreeUntilFirstHits(sequence[-1], positives,
                                                       childParents, childMap,
                                                       cladeSNPs)
        if len(refinedResults) == 0:
            solutions.append(sequence)
        else:
            print(sequence, refinedResults)
            for refRes in refinedResults:
                #print(sequence, refRes)
                seqCopy = sequence[:]
                seqCopy.append(refRes)
                refineHitsRecursively([seqCopy], positives, childParents,
                                      childMap, cladeSNPs, solutions)


def recurseDownTree(positives, childParents, childMap, cladeSNPs, solutions):
    sequences = recurseDownTreeUntilFirstHits("Adam", positives, childParents,
                                              childMap, cladeSNPs)
    newSequences = []
    for sequence in sequences:
        newSequences.append([sequence])
    refineHitsRecursively(newSequences, positives, childParents, childMap,
                          cladeSNPs, solutions)


import json


def getPanels(snpPanelConfigFile):
    snpPanelsJson = json.load(open(snpPanelConfigFile))
    yfullCladePanels = {}
    for key in snpPanelsJson:
        branches = snpPanelsJson[key]["branches"]
        for branch in branches:
            yfullCladePanels[branch.replace("*",
                                            "")] = snpPanelsJson[key]["html"]
    return yfullCladePanels


def getRankedSolutionsScratch(positives, negatives, tbCladeSNPs, tbSNPclades):
    (hierarchy, pos_clades) = createMinimalTree(positives, tbSNPclades,
                                                tbCladeSNPs)
    #print(hierarchy)
    childMap = createChildMap(hierarchy)
    #print(childMap)
    cladeSNPs = createCladeSNPs(hierarchy, tbCladeSNPs)
    #print(cladeSNPs)
    b = getRankedSolutionsSimple(pos_clades, positives, negatives, hierarchy,
                                 childMap, cladeSNPs)
    return b, hierarchy


import urllib.parse
import urllib.request


def getSNPProducts(snps):
    url = "https://www.yseq.net/catalog_json.php"
    PARAMS = {"snps": ", ".join(snps)}
    fullurl = url + "?" + urllib.parse.urlencode(PARAMS)
    data = urllib.request.urlopen(fullurl)
    a = data.read().decode("ASCII")
    snpProducts = {}
    spls = a.split(";")
    for spl in spls:
        if spl != "":
            splspl = spl.split(",")
            snpProducts[splspl[0]] = splspl[1]

    return snpProducts


def getSNPProductsTabix(snps, tbSNPClades):
    snpToProducts = {}
    for snp in snps:
        product = getProductTabix(snp, tbSNPClades)
        if product:
            snpToProducts[snp] = product
    return snpToProducts


def decodeTabixSNPs(obj):
    obj = decodeTabixSNPsThisLevel(obj)
    if "downstream" in obj:
        decodedChildren = []
        for child in obj["downstream"]:
            decodedChildren.append(decodeTabixSNPsThisLevel(child))
        obj["downstream"] = decodedChildren
    return obj


def decodeTabixSNPsThisLevel(obj):
    for encoded in obj["phyloeq"]:
        decoded = decodeTabix(encoded)
        if decoded != encoded:
            obj["phyloeq"][decoded] = obj["phyloeq"][encoded]
            obj["phyloeq"].pop(encoded)
    return obj


def decorateSNPProducts(obj, tbSNPclades):
    snps = []
    for snp in obj["phyloeq"]:
        if obj["phyloeq"][snp]["call"] == "?":
            snps.append(snp)
    if "downstream" in obj:
        for child in obj["downstream"]:
            for snp in child["phyloeq"]:
                if child["phyloeq"][snp]["call"] == "?":
                    snps.append(snp)
    if len(snps) > 0:
        products = getSNPProductsTabix(snps, tbSNPclades)
        for snp in obj["phyloeq"]:
            if snp in products:
                obj["phyloeq"][snp]["product"] = products[snp]
            if "downstream" in obj:
                for child in obj["downstream"]:
                    for snp in child["phyloeq"]:
                        if snp in products:
                            child["phyloeq"][snp]["product"] = products[snp]
    return obj


def getPanelArray(clade, snpPanelConfigFile, tbCladeSNPs, hierarchy,
                  uniqNegatives):
    panels = getPanels(snpPanelConfigFile)
    panelRootHierarchy = createMiminalTreePanelRoots(panels, tbCladeSNPs)

    panelsDownstreamPrediction = []
    panelRootsUpstreamPrediction = []
    panelsEqualToPrediction = []

    for panel in panels:
        if panel == clade:
            panelsEqualToPrediction.append(panel)
        else:
            if isUpstream(clade, panel, hierarchy):
                panelRootsUpstreamPrediction.append(panel)
            else:
                if isDownstreamPredictionAndNotBelowNegative(
                        clade, panel, uniqNegatives, panelRootHierarchy,
                        tbCladeSNPs):
                    panelsDownstreamPrediction.append(panel)

    def sortPanelRootsUpstream(panels, clade, hierarchy):
        thesorted = []
        for cld in getTotalSequence(clade, hierarchy):
            for panel in panels:
                if panel == cld:
                    thesorted.append(panel)
        if len(thesorted) == 0:
            return []
        else:
            return [thesorted[0]]

    panelArr = []
    count = 0
    for recommendedPanel in panelsEqualToPrediction:
        count = count + 1
        panelArr.append({
            "link":
            panels[recommendedPanel],
            "text":
            "Predicted " + clade +
            " is the panel root. This panel is applicable and will definitely provide higher resolution."
        })

    if count == 0:
        for recommendedPanel in sortPanelRootsUpstream(
                panelRootsUpstreamPrediction, clade, hierarchy):
            panelArr.append({
                "link":
                panels[recommendedPanel],
                "text":
                "Predicted " + clade +
                " is downstream of the panel root. This panel may be applicable if it tests subclades below "
                + clade +
                ". Please verify and check with YSEQ customer support."
            })
        for recommendedPanel in panelsDownstreamPrediction:
            panelArr.append({
                "link":
                panels[recommendedPanel],
                "text":
                "This panel may be applicable. However, absent a strong STR prediction for this clade, we recommend testing the root SNP before ordering this panel. Please verify and check with YSEQ customer support."
            })
    return panelArr


def getJSON(params, positives, negatives, tbCladeSNPsFile, tbSNPcladesFile,
            snpPanelConfigFile):
    return json.dumps(
        getJSONObject(params, positives, negatives, tbCladeSNPsFile,
                      tbSNPcladesFile, snpPanelConfigFile))


def decorateJSONObject(params, clade, score, positives, negatives, tbCladeSNPs,
                       tbSNPClades, hierarchy, snpPanelConfigFile, conflicts,
                       warning):
    theobj = {}
    clade = clade.replace("*", "")
    theobj["clade"] = clade
    if "downstream" in params:
        theobj["downstream"] = getDownstreamSNPsJSONObject(
            clade, positives, negatives, conflicts, tbCladeSNPs)
    if "phyloeq" in params:
        theobj["phyloeq"] = getCladeSNPStatusJSONObject(
            clade, positives, negatives, conflicts, tbCladeSNPs)
    if "score" in params:
        theobj["score"] = score
    if "products" in params:
        theobj = decorateSNPProducts(theobj, tbSNPClades)
    if "panels" in params and hierarchy is not None and snpPanelConfigFile is not None:
        panels = getPanelArray(clade, snpPanelConfigFile, tbCladeSNPs,
                               hierarchy, negatives)
        if len(panels) > 0:
            theobj["panels"] = panels
    if warning:
        theobj["warning"] = warning
    if "phyloeq" in params:
        return decodeTabixSNPs(theobj)
    return theobj


def getJSONForClade(params, clade, positives, negatives, tbCladeSNPsFile,
                    tbSNPcladesFile):
    return json.dumps(
        getJSONObjectForClade(params, clade, positives, negatives,
                              tbCladeSNPsFile, tbSNPcladesFile))


def getJSONObjectForClade(params, clade, positives, negatives, tbCladeSNPsFile,
                          tbSNPcladesFile):
    tbSNPclades = tabix.open(tbSNPcladesFile)
    tbCladeSNPs = tabix.open(tbCladeSNPsFile)
    uniqPositives = getUniqueSNPsetTabix(positives, tbSNPclades)
    uniqNegatives = getUniqueSNPsetTabix(negatives, tbSNPclades)
    conflicting = uniqPositives.intersection(uniqNegatives)
    uniqPositives = uniqPositives.difference(conflicting)
    uniqNegatives = uniqNegatives.difference(conflicting)
    warning = None
    if len(conflicting) > 0:
        warning = "conflicting calls for same SNP with names " + ", ".join(
            list(conflicting))
    return decorateJSONObject(params, clade, 0, uniqPositives, uniqNegatives,
                              tbCladeSNPs, tbSNPclades, None, None,
                              conflicting, warning)


def getJSONObject(params, positives, negatives, tbCladeSNPsFile,
                  tbSNPcladesFile, snpPanelConfigFile):
    tbSNPclades = tabix.open(tbSNPcladesFile)
    tbCladeSNPs = tabix.open(tbCladeSNPsFile)
    uniqPositives = getUniqueSNPsetTabix(positives, tbSNPclades)
    uniqNegatives = getUniqueSNPsetTabix(negatives, tbSNPclades)
    conflicting = uniqPositives.intersection(uniqNegatives)
    uniqPositives = uniqPositives.difference(conflicting)
    uniqNegatives = uniqNegatives.difference(conflicting)
    if len(uniqPositives) == 0:
        return {"error": "unable to determine clade due to no positive SNPs"}
    warning = None
    if len(conflicting) > 0:
        warning = "conflicting calls for same SNP with names " + ", ".join(
            list(conflicting))
    (ranked, hierarchy) = getRankedSolutionsScratch(uniqPositives,
                                                    uniqNegatives, tbCladeSNPs,
                                                    tbSNPclades)
    if "all" in params:
        result = []
        for r in ranked:
            clade = r[1]
            score = r[4]
            result.append(
                decorateJSONObject(params, clade, score, uniqPositives,
                                   uniqNegatives, tbCladeSNPs, tbSNPclades,
                                   hierarchy, snpPanelConfigFile, conflicting,
                                   warning))
        return result
    else:
        if len(ranked) > 0:
            clade = ranked[0][1]
            score = ranked[0][4]
            decorated = decorateJSONObject(params, clade, score, uniqPositives,
                                           uniqNegatives, tbCladeSNPs,
                                           tbSNPclades, hierarchy,
                                           snpPanelConfigFile, conflicting,
                                           warning)
            if len(ranked) > 1 and "score" in params:
                clade = ranked[1][1]
                score = ranked[1][4]
                decorated["nextPrediction"] = {"clade": clade, "score": score}
            return decorated
        else:
            if len(positives) == 1:
                return {
                    "error":
                    "unable to find " + list(positives)[0] +
                    " on the YFull tree"
                }
            else:
                return {
                    "error":
                    "unable to find any of " + ", ".join(positives) +
                    " on the YFull tree"
                }


def getCladeSNPStatusJSONObject(clade, positives, negatives, conflicts,
                                tbCladeSNPs):
    status = {}
    snps = getCladeSNPs(clade, tbCladeSNPs)
    poses = set(positives).intersection(snps)
    negs = set(negatives).intersection(snps)

    for snp in snps:
        status[snp] = {}
        if snp in poses:
            status[snp]["call"] = "+"
        elif snp in negs:
            status[snp]["call"] = "-"
        elif snp in conflicts:
            status[snp]["call"] = "c"
        else:
            status[snp]["call"] = "?"
    return status


def getDownstreamSNPsJSONObject(clade, positives, negatives, conflicts,
                                tbCladeSNPs):
    children = getChildrenTabix(clade, tbCladeSNPs)
    downstreamNodes = []
    for child in children:
        downstreamNode = {"clade": child}

        downstreamNode["phyloeq"] = getCladeSNPStatusJSONObject(
            child, positives, negatives, conflicts, tbCladeSNPs)
        grandChildren = getChildrenTabix(child, tbCladeSNPs)
        if len(grandChildren) > 0:
            downstreamNode["children"] = len(grandChildren)
        downstreamNodes.append(downstreamNode)
    return downstreamNodes


def findCladeRefactored(positives, negatives, tbCladeSNPsFile, tbSNPcladesFile,
                        snpPanelConfigFile):
    obj = getJSONObject("all,phyloeq,downstream,score", positives, negatives,
                        tbCladeSNPsFile, tbSNPcladesFile)
    if len(obj) > 0:
        html = "<table><tr><td>Clade</td><td>Score</td></tr>"
        for res in obj:
            if "clade" in res:
                if res["clade"] != "unable to determine":
                    html = html + '<tr><td><a href="https://www.yfull.com/tree/' + res[
                        "clade"] + '">' + res["clade"] + "</a></td><td>" + str(
                            round(res["score"], 3)) + "</td></tr>"
                else:
                    html = html + '<tr><td>unable to determine</td><td></td></tr>'
        html = html + "</table>"
        panels = getPanels(snpPanelConfigFile)
        tbCladeSNPs = tabix.open(tbCladeSNPsFile)
        tbSNPclades = tabix.open(tbSNPcladesFile)
        panelRootHierarchy = createMiminalTreePanelRoots(panels, tbCladeSNPs)
        panelsDownstreamPrediction = []
        panelRootsUpstreamPrediction = []
        panelsEqualToPrediction = []

        uniqPositives = getUniqueSNPsetTabix(positives, tbSNPclades)
        uniqNegatives = getUniqueSNPsetTabix(negatives, tbSNPclades)

        (hierarchy, _) = createMinimalTree(positives, tbSNPclades, tbCladeSNPs)

        bestClade = obj[0]["clade"]
        for panel in panels:
            if panel == bestClade:
                panelsEqualToPrediction.append(panel)
            else:
                if isUpstream(bestClade, panel, hierarchy):
                    panelRootsUpstreamPrediction.append(panel)
                else:
                    if isDownstreamPredictionAndNotBelowNegative(
                            bestClade, panel, uniqNegatives,
                            panelRootHierarchy, tbCladeSNPs):
                        panelsDownstreamPrediction.append(panel)

        def sortPanelRootsUpstream(panels, clade, hierarchy):
            thesorted = []
            for cld in getTotalSequence(clade, hierarchy):
                for panel in panels:
                    if panel == cld:
                        thesorted.append(panel)
            if len(thesorted) == 0:
                return []
            else:
                return [thesorted[0]]

        html = html + "<br><br><b>Recommended Panels</b><br><br>"
        count = 0
        for recommendedPanel in panelsEqualToPrediction:
            count = count + 1
            html = html + str(count) + ". " + panels[
                recommendedPanel] + "<br><br><i>Predicted " + bestClade + " is the panel root. This panel is applicable and will definitely provide higher resolution.</i><br><br>"

        if count == 0:
            for recommendedPanel in sortPanelRootsUpstream(
                    panelRootsUpstreamPrediction, bestClade, hierarchy):
                count = count + 1
                html = html + str(count) + ". " + panels[
                    recommendedPanel] + "<br><br><i>Predicted " + bestClade + " is downstream of the panel root. This panel may be applicable if it tests subclades below " + bestClade + ". Please verify and check with YSEQ customer support.</i><br><br>"
            for recommendedPanel in panelsDownstreamPrediction:
                count = count + 1
                html = html + str(count) + ". " + panels[
                    recommendedPanel] + "<br><br><i>Subject has not tested positive for any SNP in this panel, including the root. Absent a strong STR prediction for this clade, we recommend testing the root SNP before ordering this panel.</i><br><br>"

            #2nd Phase Development - get panel SNPs from API: html = html + "<br>" + getSNPpanelStats(b[0][1], panel, tbSNPclades, tbCladeSNPs) + "<br>"
        html = html + "<br><br>" + createSNPStatusHTML(
            bestClade, uniqPositives, uniqNegatives, tbCladeSNPs)
    print(html)


def isUpstream(predictedClade, panelRoot, hierarchyForClade):
    sequence = getTotalSequence(predictedClade, hierarchyForClade)
    passed = False
    for clade in sequence:
        if not passed:
            if clade == panelRoot:
                passed = True
    return passed


def isDownstreamPredictionAndNotBelowNegative(predictedClade, panelRoot,
                                              negatives, hierarchy,
                                              tbCladeSNPs):
    sequence = getTotalSequence(panelRoot, hierarchy)
    passed = False
    failed = False
    for clade in sequence:
        if not failed and not passed:
            snps = set(getCladeSNPs(clade, tbCladeSNPs))
            intersects = len(snps.intersection(negatives))
            if intersects == 0:
                if predictedClade == clade:
                    passed = True
            else:
                failed = True
    return passed


def getSNPStatus(snp):
    return "Query YSEQ for ordering status of SNP"


def createSNPStatusHTML(clade, positives, negatives, tbCladeSNPs):
    children = getChildrenTabix(clade, tbCladeSNPs)
    snpStatus = {}
    for child in children:
        snps = getCladeSNPs(child, tbCladeSNPs)
        poses = set(positives).intersection(snps)
        negs = set(negatives).intersection(snps)
        status = "uncertain"
        if len(poses) > 0 and len(negs) > 0:
            status = "Split Result: " + ", ".join(
                poses) + " positive, " + ", ".join(negs) + " negative"
        else:
            if len(poses) > 0:
                status = "Positive due to " + ", ".join(poses) + " positive"
            else:
                if len(negs) > 0:
                    status = "Negative due to " + ", ".join(negs) + " negative"
                else:
                    status = getSNPStatus(child)
        snpStatus[child] = status
    if len(children) > 0:
        html = "<b>Downstream Lineages</b><br><br><table><tr><td>Clade</td><td>Status</td></tr>"
        for child in children:
            html = html + "<tr><td>" + child + "</td><td>" + snpStatus[
                child] + "</td></tr>"
        html = html + "</table>"
    else:
        html = "<b>No Downstream Lineages Yet Discovered</b>"
    return html


def getPanelSNPs(panel):
    return [
        "M241", "L283", "Z2432", "Z1297", "Z1295", "CTS15058", "CTS6190",
        "Z631", "Z1043", "Y87609", "PH1553", "Y26712", "Y32998", "Y29720",
        "Z8424", "Y98609", "M102"
    ]


def getCladesFromSNPpanel(snps, panel, tbSNPclades):
    clades = []
    unknownPanelSNPs = []
    for snp in snps:
        theclades = getSNPClades(snp, tbSNPclades)
        if len(theclades) == 1:
            clades.append(theclades[0])
        else:
            if len(theclades) > 1:
                for clade in theclades:
                    if clade[0] == panel[0]:
                        clades.append(clade)
            else:
                unknownPanelSNPs.append(snp)
    return clades


def recurseDownCladeWithinPanel(clade, childMap, panelClades, possible):
    if clade in childMap:
        for child in childMap[clade]:
            recurseDownCladeWithinPanel(child, childMap, panelClades, possible)
    if clade in panelClades:
        possible.append(clade)


def getSNPpanelStats(predictedClade, panelRootClade, tbSNPclades, tbCladeSNPs):
    panelSNPs = getPanelSNPs(panelRootClade)
    panelClades = getCladesFromSNPpanel(panelSNPs, panelRootClade, tbSNPclades)

    hier = {}
    for clade in panelClades:
        recurseToRootAddParents(clade, hier, tbCladeSNPs)

    childMap = createChildMap(hier)

    panelPositiveClades = []

    curr = predictedClade

    while curr in hier and curr != panelRootClade:
        if curr in panelClades:
            panelPositiveClades.append(curr)
        curr = hier[curr]

    if curr == panelRootClade:
        panelPositiveClades.append(curr)

    possibleRemaining = []

    recurseDownCladeWithinPanel(predictedClade, childMap, panelClades,
                                possibleRemaining)
    if predictedClade in possibleRemaining:
        possibleRemaining.remove(predictedClade)

    #maximumTestsToTerminalSubclade = None
    #meanTestsToTerminalSubcladeGivenNoAprioris = None
    #expectedTestsToTerminalSubcladeGivenYFullAprioris = None
    return "PH1553 clades: " + str(getCladeSNPs(
        "PH1553", tbCladeSNPs)) + ", panelClades: " + str(
            panelClades) + ", total positive: " + str(
                panelPositiveClades) + ", possible remaining: " + str(
                    possibleRemaining)


#def isDownstreamPredictionAndNotBelowNegative(predictedClade, panelRoot, negatives, childMap, tbCladeSNPs):
#    children = getChildren(predictedClade, childMap)
#    passes = False
#    for child in children:
#        snps = set(getCladeSNPs(child, tbCladeSNPs))
#        intersects = len(snps.intersection(negatives))
#        if intersects == 0:
#            passes = passes or isDownstreamPredictionAndNotBelowNegative(child, panelRoot, negatives, childMap, tbCladeSNPs)
#
#
#def recommendPanel(prediction, positives, negatives):
#    allpanels = {}
#    for panel in allpanels:
