#!/usr/bin/env python3
from __future__ import absolute_import, division, print_function
#   Author: Richard Ziga based on Jeremy Schulman's code
#
#   This code is free software: you can redistribute it and/or modify
#   it under the terms of the MIT License.
#
#   The author provides no warranties regarding the software, which is
#   provided "AS-IS" and your use of this software is entirely at your
#   own risk.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR DAMAGES OF ANY
#   KIND RELATING TO USE OF THE SOFTWARE, INCLUDING WITHOUT LIMITATION
#   ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#   DAMAGES; ANY PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#   DATA, OR PROFITS; OR BUSINESS INTERRUPTION, HOWEVER CAUSED AND ON ANY
#   THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#   (INCLUDING NEGLIGENCE), EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import jinja2
import csv

TEMPLATE_FILENAME = 'routerXE.j2'
CSVDATA_FILENAME = 'input_router.csv'

# # ---------------------------------------------------------------------------
# #  iterate through the values in the csv file for routing protocols
# # ---------------------------------------------------------------------------


def transform_vlan_data(row):
    # remove all fields that start with eigrp
    # "eigrp_" from the original dictionary.  we only want to keep the
    # fields that do not have a value of "0" as the csv-data uses "0" to
    # indicate a non-used vlan.  The result is a dictionary.
    # # # EIGRP
    eigrp_fields = {
        field_name: field_value
        for field_name, field_value in row.copy().items()
        if field_name.startswith('eigrp_') and row.pop(field_name)
        if field_value != '0'
    }

    # this works fine

    row['eigrp'] = {
        eigrp_fields[f].replace(' ', '_'): eigrp_fields[f.replace('network',
                                                        'mask')]
        for f in eigrp_fields if f.startswith('eigrp_network')
    }

# # # OSPF
    ospf_fields = {
        field_name: field_value
        for field_name, field_value in row.copy().items()
        if field_name.startswith('ospf_') and row.pop(field_name)
        if field_value != '0'
    }

    # this works fine

    row['ospf'] = {
        ospf_fields[f].replace(' ', '_',): ospf_fields[f.replace('network',
                                                                 'maskarea')]
        for f in ospf_fields if f.startswith('ospf_network')
    }

# # # BGP
    bgp_fields = {
        field_name: field_value
        for field_name, field_value in row.copy().items()
        if field_name.startswith('bgp_') and row.pop(field_name)
        if field_value != '0'
    }

    # 

    row['bgp'] = {
        bgp_fields[f].replace(' ', '_'): bgp_fields[f.replace('network',
                                                              'mask')]
        for f in bgp_fields if f.startswith('bgp_network')
    }

# # # BGP remote Neighbors
    bgpr_fields = {
        field_name: field_value
        for field_name, field_value in row.copy().items()
        if field_name.startswith('bgpr_') and row.pop(field_name)
        if field_value != '0'
    }

    # what I found here was that you don't want the second argument (remas)
    # to start with remote 

    row['bgpr'] = {
        bgpr_fields[f].replace(' ', '_'): bgpr_fields[f.replace('remote',
                                                                'remas')]
        for f in bgpr_fields if f.startswith('bgpr_remote')
    }
# # # NTP
    ntp_fields = {
        field_name: field_value
        for field_name, field_value in row.copy().items()
        if field_name.startswith('ntp_') and row.pop(field_name)
        if field_value != '0'
    }

    # this works fine

    row['ntp'] = {
        ntp_fields[f].replace(' ', '_'): ntp_fields[f.replace('pop', 'server')]
        for f in ntp_fields if f.startswith('ntp_pop')
    }

# # # 
# # ---------------------------------------------------------------------------
# # create a jinja2 environment and load the template file
# # ---------------------------------------------------------------------------


env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.getcwd()),
    trim_blocks=True, lstrip_blocks=True)

template = env.get_template(TEMPLATE_FILENAME)

# # ---------------------------------------------------------------------------
# # now read the CSV file, processing each row, and creating a
# # rendered file for each 'hostname'
# # ---------------------------------------------------------------------------

for row in csv.DictReader(open(CSVDATA_FILENAME)):
    transform_vlan_data(row)
    with open(row['hostname'] + '.txt', 'w+') as f:
        f.write(template.render(row))
