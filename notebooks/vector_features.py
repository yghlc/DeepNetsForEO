#!/usr/bin/env python3
# Filename: vector_features 
"""
introduction: shapefile operation based on pyshp

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 28 October, 2016
"""

from optparse import OptionParser
import basic_src.basic as basic
import basic_src.io_function as io_function
import os,sys
import numpy

# import  parameters

#pyshp library
import shapefile

#rasterstats
from rasterstats import zonal_stats

from shapely.geometry import Polygon
from shapely.ops import cascaded_union

class shape_opeation(object):

    def __init__(self):
        # self.__qgis_app = None # qgis environment

        pass


    def __del__(self):
        # if self.__qgis_app is not None:
        #     basic.outputlogMessage("Release QGIS resource")
        #     self.__qgis_app.exitQgis()
        pass

    def __find_field_index(self,all_fields, field_name):
        """
        inquire the index of specific field_name in the all fields
        :param all_fields: all fields
        :param field_name: specific field name
        :return: index of specific field name if successful, False Otherwise
        """

        field_name_index = -1
        field_len = len(all_fields)
        for t_index in range(0,field_len):
            t_field = all_fields[t_index]
            if isinstance(t_field, tuple):
                # t_index += 1  occur once
                continue
            if field_name == t_field[0]:
                field_name_index = t_index - 1  # first field not show in records
                break
        if field_name_index < 0:
            basic.outputlogMessage('error, attribute %s not found in the fields' % field_name)
            return False
        return field_name_index

    def has_field(self,input_shp,field_name):
        """
        inquires whether the shape file contains the specific field given by the field name
        :param input_shp: shape file path
        :param field_name: the name of the specific field
        :return: True if exist, False otherwise
        """
        if io_function.is_file_exist(input_shp) is False:
            return False
        try:
            org_obj = shapefile.Reader(input_shp)
        except IOError:
            basic.outputlogMessage(str(IOError))
            return False
        all_fields = org_obj.fields
        field_len = len(all_fields)

        for t_index in range(0, field_len):
            t_field = all_fields[t_index]
            if isinstance(t_field, tuple):
                # t_index += 1  occur once
                continue
            if field_name == t_field[0]:
                return True  #find the specific field of the given name

        return False



    def get_polygon_shape_info(self, input_shp, out_box, bupdate=False):
        """
        get Oriented minimum bounding box for a polygon shapefile,
        and update the shape information based on oriented minimum bounding box to
        the input shape file
        :param input_shp: input polygon shape file
        :param out_box: output Oriented minimum bounding box shape file
        :param bupdate: indicate whether update the original input shapefile
        :return:True is successful, False Otherwise
        """
        if io_function.is_file_exist(input_shp) is False:
            return False
        args_list = ['qgis_function.py',input_shp,out_box]
        if basic.exec_command_args_list_one_file(args_list, out_box) is False:
            basic.outputlogMessage('get polygon shape information of %s failed' % input_shp)
            return False
        else:
            basic.outputlogMessage('get polygon shape information of %s completed, output file is %s' % (input_shp, out_box))
            return True

        # update shape info to input shape file
        # if bupdate is True:
        #     pass

    def get_shapes_count(self,input_shp):
        """
        get the number of shape in the shape file
        :param input_shp: path of shape file
        :return: the number of shape (polygon, points), Fasle Otherwise
        """
        if io_function.is_file_exist(input_shp) is False:
            return False
        try:
            org_obj = shapefile.Reader(input_shp)
        except IOError:
            basic.outputlogMessage(str(IOError))
            return False
        return len(org_obj.shapes())


    def add_fields_shape(self,ori_shp,new_shp,output_shp):
        """
        add fields from another shapefile(merge the fields of two shape files), the two shape files should have the same number of features
        :param ori_shp: the path of original shape file which will be added new field
        :param new_shp: the shape file contains new fields
        :output_shp: saved shape file
        :return:True if successful, False otherwise

        """
        # Read in our existing shapefile
        if io_function.is_file_exist(ori_shp) is False or io_function.is_file_exist(new_shp) is False:
            return False
        try:
            org_obj = shapefile.Reader(ori_shp)
            new_obj = shapefile.Reader(new_shp)
        except IOError:
            basic.outputlogMessage(str(IOError))
            return False

        if len(org_obj.shapes()) != len(new_obj.shapes()):
            basic.outputlogMessage("error: the input two shape file do not have the same number of features")
            return False
        if org_obj.shapeType != new_obj.shapeType:
            basic.outputlogMessage("error: the input two shape file have different shapeType")
            return False

        # Create a new shapefile in memory
        w = shapefile.Writer()
        w.shapeType = org_obj.shapeType

        # Copy over the existing fields
        w.fields = list(org_obj.fields)
        for t_field in list(new_obj.fields):
            if isinstance(t_field,tuple):
                continue
            w.fields.append(t_field)


        # Add our new field using the pyshp API
        # w.field("KINSELLA", "C", "40")

        # # We'll create a counter in this example
        # # to give us sample data to add to the records
        # # so we know the field is working correctly.
        # i = 1
        #
        # Loop through each record, add a column.  We'll
        # insert our sample data but you could also just
        # insert a blank string or NULL DATA number
        # as a place holder
        org_records = org_obj.records()
        new_records = new_obj.records()
        for i in range(0,len(org_records)):
            rec = org_records[i]
            for value in new_records[i]:
                rec.append(value)

            # Add the modified record to the new shapefile
            w.records.append(rec)

        # Copy over the geometry without any changes
        w._shapes.extend(org_obj.shapes())

        # copy prj file
        org_prj = os.path.splitext(ori_shp)[0]+".prj"
        out_prj = os.path.splitext(output_shp)[0]+".prj"
        io_function.copy_file_to_dst(org_prj,out_prj,overwrite=True)

        # Save as a new shapefile (or write over the old one)
        w.save(output_shp)

        pass

    def add_one_field_records_to_shapefile(self,shape_file,record_value,field_name,field_type=None):
        """
        add one field and records to shape file (add one column to attributes table)
        :param shape_file: shape file path
        :param record_value: a list contians the records value
        :param field_name: field name (the column title)
        :param field_type:  field type, eg. float, int, string,  can read from type(record_value[0])
        :return:True is successful, Flase otherwise
        """
        if io_function.is_file_exist(shape_file) is False:
            return False
        if isinstance(record_value,list) is False:
            basic.outputlogMessage('record_value must be list')

        records_count = len(record_value)
        if(records_count<1):
            basic.outputlogMessage('error, no input records')
            return False

        try:
            org_obj = shapefile.Reader(shape_file)
        except :
            basic.outputlogMessage(str(IOError))
            return False
        if len(org_obj.shapes()) != records_count:
            basic.outputlogMessage("error: the input field_name_value do not have the same number of features")
            return False

        # Create a new shapefile in memory
        w = shapefile.Writer()
        w.shapeType = org_obj.shapeType

        # Copy over the existing fields
        w.fields = list(org_obj.fields)

        #check whether the field name already exist
        exist_index = -1
        for i in range(0,len(w.fields)):
            if w.fields[i][0] == field_name:
                exist_index = i - 1   # -1 means ignore the 'DeletionFlag' (first column)
                basic.outputlogMessage('warning, field name: %s already in table %d (first column is 0) column, '
                                       'this will replace the original value'%(field_name,exist_index))
                break
        if exist_index >= 0:
            pass
        else:
            #create a new fields at the last
            first_record = record_value[0]
            if isinstance(first_record,float):
                attr_list = [field_name, 'N',24,10]
            elif isinstance(first_record, int):
                attr_list = [field_name, 'N', 24, 0]
            elif isinstance(first_record, str):
                attr_list = [field_name, 'C', 20, 0]
            else:
                basic.outputlogMessage('error, unsupport data type')
                return False
            # attr_list = [field_name, 'N', 24, 0]
            w.fields.append(attr_list)


        org_records = org_obj.records()
        if exist_index >= 0:
            for i in range(0, len(org_records)):
                rec = org_records[i]
                rec[exist_index] = record_value[i]
                # Add the modified record to the new shapefile
                w.records.append(rec)
        else:
            for i in range(0, len(org_records)):
                rec = org_records[i]
                rec.append(record_value[i])
                # Add the modified record to the new shapefile
                w.records.append(rec)

        # check field whose type is str and convert bytes to str (fill NULL) if applicable
        str_filed_index = []
        for i in range(0, len(w.fields)):
            if w.fields[i][1] == 'C':
                str_filed_index.append(i - 1)  # -1 means ignore the 'DeletionFlag' (first column)
        if len(str_filed_index)>0:
            for i in range(0,len(w.records)):
                for j in str_filed_index:
                    if isinstance(w.records[i][j],bytes):
                        w.records[i][j] = 'NULL'

        # Copy over the geometry without any changes
        w._shapes.extend(org_obj.shapes())

        # copy prj file
        # org_prj = os.path.splitext(ori_shp)[0] + ".prj"
        # out_prj = os.path.splitext(output_shp)[0] + ".prj"
        # io_function.copy_file_to_dst(org_prj, out_prj,overwrite=True)

        # overwrite original file
        w.save(shape_file)

        return True



    def add_fields_to_shapefile(self,shape_file,field_name_value,prefix):
        """
        add one new field and its records to shape file, currently, the records value must be digital number
        :param shape_file: the shape file for adding new fields
        :param field_name_value: a list contains records value of this fields
        :param prefix: first part of field name, eg. "prefix_key"
        :return: True if successful, False otherwise
        """
        if io_function.is_file_exist(shape_file) is False:
            return False
        if isinstance(field_name_value,list) is False:
            basic.outputlogMessage('field_name_value must be list')

        records_count = len(field_name_value)
        if(records_count<1):
            basic.outputlogMessage('error, no input records')
            return False

        try:
            org_obj = shapefile.Reader(shape_file)
        except :
            basic.outputlogMessage(str(IOError))
            return False
        if len(org_obj.shapes()) != records_count:
            basic.outputlogMessage("error: the input field_name_value do not have the same number of features")
            return False

        # Create a new shapefile in memory
        w = shapefile.Writer()
        w.shapeType = org_obj.shapeType

        # Copy over the existing fields
        w.fields = list(org_obj.fields)
        first_record = field_name_value[0]
        for t_key in first_record.keys():
            # if isinstance(t_field, tuple):
            #     continue
            attr_list = [prefix +'_'+ t_key, 'N',24,5] #prefix + t_key  #["name", type,max_length, showed_length] only accept digital number now
            w.fields.append(attr_list)

        org_records = org_obj.records()

        for i in range(0, len(org_records)):
            rec = org_records[i]
            dict_in=field_name_value[i]

            for t_key in dict_in.keys():
                rec.append(dict_in.get(t_key))

            # Add the modified record to the new shapefile
            w.records.append(rec)

        # Copy over the geometry without any changes
        w._shapes.extend(org_obj.shapes())

        # copy prj file
        # org_prj = os.path.splitext(ori_shp)[0] + ".prj"
        # out_prj = os.path.splitext(output_shp)[0] + ".prj"
        # io_function.copy_file_to_dst(org_prj, out_prj,overwrite=True)

        # overwrite original file
        w.save(shape_file)

        return True


    def add_fields_from_raster(self,ori_shp,raster_file,field_name,band=1):
        """
        get field value from raster file by using "rasterstats"

        """
        if io_function.is_file_exist(ori_shp) is False or io_function.is_file_exist(raster_file) is False:
            return False
        # stats_list = ['min', 'max', 'mean', 'count','median','std']
        stats_list = ['mean', 'std']
        # band = 1
        stats = zonal_stats(ori_shp,raster_file,band = band,stats = stats_list)
        #test
        # for tp in stats:
        #     print("mean:",tp["mean"],"std:",tp["std"])

        if self.add_fields_to_shapefile(ori_shp, stats, field_name) is False:
            basic.outputlogMessage('add fields to shape file failed')

        return True

    def remove_shape_baseon_field_value(self,shape_file,out_shp,class_field_name,threashold,smaller=True):
        """
        remove features from shapefile based on the field value,
        if smaller is true, then the value smaller than threashold will be removed
        if smaller is False, then the value greater than threashold will be remove
        :param shape_file: input shape file
        :param out_shp: saved shape file
        :param class_field_name: the name of class field, such as area
        :param threashold: threashold value
        :param smaller:  if smaller is true, then the value smaller than threashold will be removed,
        :return: True if successful, False otherwise
        """
        if io_function.is_file_exist(shape_file) is False:
            return False

        try:
            org_obj = shapefile.Reader(shape_file)
        except:
            basic.outputlogMessage(str(IOError))
            return False

        # Create a new shapefile in memory
        w = shapefile.Writer()
        w.shapeType = org_obj.shapeType

        org_records = org_obj.records()
        if (len(org_records) < 1):
            basic.outputlogMessage('error, no record in shape file ')
            return False

        # Copy over the geometry without any changes
        w.fields = list(org_obj.fields)
        field_index = self.__find_field_index(w.fields, class_field_name)
        if field_index is False:
            return False
        shapes_list = org_obj.shapes()
        i = 0
        removed_count = 0
        if smaller is True:
            for i in range(0,len(shapes_list)):
                rec = org_records[i]
                if rec[field_index] < threashold:    # remove the record which is smaller than threashold
                    removed_count = removed_count +1
                    continue
                w._shapes.append(shapes_list[i])
                rec = org_records[i]
                w.records.append(rec)
        else:
            for i in range(0, len(shapes_list)):
                rec = org_records[i]
                if rec[field_index] >  threashold:  # remove the record which is greater than threashold
                    removed_count = removed_count +1
                    continue
                w._shapes.append(shapes_list[i])
                rec = org_records[i]
                w.records.append(rec)

        basic.outputlogMessage('Remove polygons based on %s, total count: %d' % (class_field_name,removed_count))
        # w._shapes.extend(org_obj.shapes())

        # copy prj file
        org_prj = os.path.splitext(shape_file)[0] + ".prj"
        out_prj = os.path.splitext(out_shp)[0] + ".prj"
        io_function.copy_file_to_dst(org_prj, out_prj,overwrite=True)

        w.save(out_shp)
        return True

    def remove_nonclass_polygon(self,shape_file,out_shp,class_field_name):
        """
        remove polygons that are not belong to targeted class, it means the value of class_field_name is 0
        :param shape_file: input shapefile containing all the polygons
        :param out_shp: output shapefile
        :param class_field_name: the name of class field, such as svmclass, treeclass
        :return: True if successful, False Otherwise
        """
        if io_function.is_file_exist(shape_file) is False:
            return False

        try:
            org_obj = shapefile.Reader(shape_file)
        except:
            basic.outputlogMessage(str(IOError))
            return False

        # Create a new shapefile in memory
        w = shapefile.Writer()
        w.shapeType = org_obj.shapeType

        org_records = org_obj.records()
        if (len(org_records) < 1):
            basic.outputlogMessage('error, no record in shape file ')
            return False

        # Copy over the geometry without any changes
        w.fields = list(org_obj.fields)
        field_index = self.__find_field_index(w.fields, class_field_name)
        if field_index is False:
            return False
        shapes_list = org_obj.shapes()
        i = 0
        removed_count = 0
        for i in range(0,len(shapes_list)):
            rec = org_records[i]
            if rec[field_index] == 0:       # remove the record which class is 0, 0 means non-gully
                removed_count = removed_count +1
                continue

            w._shapes.append(shapes_list[i])
            rec = org_records[i]
            w.records.append(rec)

        basic.outputlogMessage('Remove non-class polygon, total count: %d'%removed_count)
        # w._shapes.extend(org_obj.shapes())

        # copy prj file
        org_prj = os.path.splitext(shape_file)[0] + ".prj"
        out_prj = os.path.splitext(out_shp)[0] + ".prj"
        io_function.copy_file_to_dst(org_prj, out_prj,overwrite=True)

        w.save(out_shp)
        return True



    def get_shape_records_value(self,input_shp,attributes=None):
        """
        get several fields value of shape file
        :param input_shp: shape file path
        :param attributes: a list contains the field name want to read
        :return: a 2D list contains the records value of the several fields.
        """
        #  read existing shape file
        if io_function.is_file_exist(input_shp) is False:
            return False
        attributes_value = [] # 2 dimensional
        attributes_index = [] # 1 dimensional

        try:
            org_obj = shapefile.Reader(input_shp)
        except IOError:
            basic.outputlogMessage(str(IOError))
            return False
        all_fields = org_obj.fields

        # test
        # txt_obj = open('attributes.txt','w')
        # outstr=''


        if attributes is None:
            # return all attribute values
            all_records = org_obj.records()
            return all_records
        elif isinstance(attributes,list):
            # return selected attributes
            field_len = len(all_fields)
            sel_attrib_len = len(attributes)
            attributes_index = [-1]*sel_attrib_len
            for sel_index in range(0, sel_attrib_len):
                sel_attrib = attributes[sel_index]
                for t_index in range(0,field_len):
                    t_field = all_fields[t_index]
                    if isinstance(t_field, tuple):
                        # t_index += 1  occur once
                        continue
                    if sel_attrib == t_field[0]:
                        attributes_index[sel_index] = t_index - 1  # first field not show in records
                        break

            # check whether all the attributes are found
            b_attribute_not_found = False
            for sel_index in range(0, sel_attrib_len):
                if attributes_index[sel_index] == -1:
                    b_attribute_not_found = True
                    basic.outputlogMessage('error, attribute %s not found in the fields'%attributes[sel_index])
            if b_attribute_not_found:
                return False
        else:
            basic.outputlogMessage('error, input attributes list is not correct')
            return False

        all_records = org_obj.records()

        for i in range(0, len(all_records)):
            rec = all_records[i]
            # sel_attrib_value = []
            # for j in attributes_index:
            #     if isinstance(rec[j],bytes):
            #         sel_attrib_value.append("NULL")
            #     else:
            #         sel_attrib_value.append(rec[j])
            sel_attrib_value = [rec[j] for j in attributes_index]
            attributes_value.append(sel_attrib_value)

        return attributes_value

    def save_attributes_values_to_text(self,attributes_values,out_file):
        """
        save attributes values (2D list) to text file
        :param attributes_values: 2D list attributes values (records count , nfeature)
        :param out_file: save file path
        :return: True is successful, False otherwise
        """
        if isinstance(attributes_values,list) is False:
            basic.outputlogMessage('input attributes_values must be list')
            return False

        if attributes_values is not False:
            f_obj = open(out_file, 'w')
            for record in attributes_values:
                out_str = ''
                for value in record:
                    if isinstance(value, float):
                        out_str += '%.2f' % value + '\t'
                    elif isinstance(value, bytes):
                        out_str += 'NULL' + '\t'  # str(value,'utf-8') + '\t'
                    else:
                        out_str += str(value) + '\t'
                        # if value=='gully':
                        #     test = 1
                f_obj.writelines(out_str + '\n')
            f_obj.close()

        return True


def shape_from_shapely_to_pyshp(shapely_shape,keep_holes=True):
    """
    convert shape object in the shapely object to pyshp object (shapefile)
    Note however: the function will NOT handle any interior polygon holes if there are any,
    it simply ignores them.
    :param shapely_shape: the shapely object
    :return: object if successful, False otherwise
    """
    # first convert shapely to geojson
    try:
        shapelytogeojson = shapely.geometry.mapping
    except:
        import shapely.geometry
        shapelytogeojson = shapely.geometry.mapping
    geoj = shapelytogeojson(shapely_shape)
    # create empty pyshp shape
    record = shapefile._Shape()
    # set shapetype
    if geoj["type"] == "Null":
        pyshptype = 0
    elif geoj["type"] == "Point":
        pyshptype = 1
    elif geoj["type"] == "LineString":
        pyshptype = 3
    elif geoj["type"] == "Polygon":
        pyshptype = 5
    elif geoj["type"] == "MultiPoint":
        pyshptype = 8
    elif geoj["type"] == "MultiLineString":
        pyshptype = 3
    elif geoj["type"] == "MultiPolygon":
        pyshptype = 5
    record.shapeType = pyshptype
    # set points and parts
    if geoj["type"] == "Point":
        record.points = geoj["coordinates"]
        record.parts = [0]
    elif geoj["type"] in ("MultiPoint","Linestring"):
        record.points = geoj["coordinates"]
        record.parts = [0]
    elif geoj["type"] in ("Polygon"):
        if keep_holes is False:
            record.points = geoj["coordinates"][0]
            record.parts = [0]
        else:
            # need to consider the holes
            all_coordinates = geoj["coordinates"];
            parts_count = len(all_coordinates)
            # print(parts_count)
            record.parts = []
            for i in range(0,parts_count):
                # record.points = geoj["coordinates"][0]
                record.parts.append(len(record.points))
                record.points.extend(all_coordinates[i])


    elif geoj["type"] in ("MultiPolygon","MultiLineString"):
        if keep_holes is False:
            index = 0
            points = []
            parts = []
            for eachmulti in geoj["coordinates"]:
                points.extend(eachmulti[0])
                parts.append(index)
                index += len(eachmulti[0])
            record.points = points
            record.parts = parts
        else:
            # need to consider the holes
            all_polygons_coor = geoj["coordinates"]
            polygon_count = len(all_polygons_coor)
            # print(parts_count)
            record.parts = []
            for i in range(0, polygon_count):
                for j in range(0,len(all_polygons_coor[i])):
                    # record.points = geoj["coordinates"][0]
                    record.parts.append(len(record.points))
                    record.points.extend(all_polygons_coor[i][j])


        # index = 0
        # points = []
        # parts = []
        # skip = 1
        # for eachmulti in geoj["coordinates"]:
        #     if skip ==1 :
        #         skip = skip + 1
        #         continue
        #
        #     points.extend(eachmulti[0])
        #     parts.append(index)
        #     index += len(eachmulti[0])
        # record.points = points
        # record.parts = parts
    return record

def shape_from_pyshp_to_shapely(pyshp_shape):
    """
     convert pyshp object to shapely object
    :param pyshp_shape: pyshp (shapefile) object
    :return: shapely object if successful, False otherwise
    """

    if pyshp_shape.shapeType is 5:  # Polygon or multiPolygon
        parts_index = pyshp_shape.parts
        if len(parts_index) < 2:
            # Create a polygon with no holes
            record = Polygon(pyshp_shape.points)
        else:
            # Create a polygon with one or several holes
            seperate_parts = []
            parts_index.append(len(pyshp_shape.points))
            for i in range(0, len(parts_index)-1):
                points = pyshp_shape.points[parts_index[i]:parts_index[i+1]]
                seperate_parts.append(points)
            exterior = seperate_parts[0]  # assuming the first part is exterior
            interiors = [seperate_parts[i] for i in range(1,len(seperate_parts))]
            record = Polygon(shell=exterior,holes=interiors)
    else:
        basic.outputlogMessage('have not complete, other type of shape is not consider!')
        return False

    # # plot shape for checking
    # from matplotlib import pyplot as plt
    # from descartes import PolygonPatch
    # from math import sqrt
    # # from shapely.geometry import Polygon, LinearRing
    # # from shapely.ops import cascaded_union
    # BLUE = '#6699cc'
    # GRAY = '#999999'
    #
    # # plot these two polygons separately
    # fig = plt.figure(1,  dpi=90) #figsize=SIZE,
    # ax = fig.add_subplot(111)
    # poly1patch = PolygonPatch(record, fc=BLUE, ec=BLUE, alpha=0.5, zorder=2)
    # # poly2patch = PolygonPatch(polygon2, ec=BLUE, alpha=0.5, zorder=2)
    # ax.add_patch(poly1patch)
    # # ax.add_patch(poly2patch)
    # boundary = record.bounds
    # xrange = [boundary[0], boundary[2]]
    # yrange = [boundary[1], boundary[3]]
    # ax.set_xlim(*xrange)
    # # ax.set_xticks(range(*xrange) + [xrange[-1]])
    # ax.set_ylim(*yrange)
    # # ax.set_yticks(range(*yrange) + [yrange[-1]])
    # # ax.set_aspect(1)
    #
    # plt.show()



    return record

def get_area_length_geometric_properties(shapely_polygons):
    """
    get the area, length, and other geometric properties of polygons (shapely object)
    :param shapely_polygons: a list contains the shapely object
    :return: list of area and length (perimeter)
    """
    area = []
    length = [] #(perimeter of polygon)

    if len(shapely_polygons) < 1:
        basic.outputlogMessage('error, No input polygons')
        return area, length    #  area and length is none

    for polygon in shapely_polygons:
        area_value = polygon.area
        length_value = polygon.length
        area.append(abs(area_value))   # area_value could be negative for a irregular polygons
        length.append(length_value)


    return area, length


def merge_touched_polygons(polygon_list,adjacent_matrix):
    """
    merge all the connected (touched, ) polygons into one polygon
    :param polygon_list: a list containing at least two polygons, shapely object not pyshp object
    :param adjacent_matrix: the matrix storing the touching relationship of all the polygons
    :return: a polygon list after merging if successful, False Otherwise
    """
    count = len(polygon_list)
    matrix_size = adjacent_matrix.shape
    merged_polygons = []
    if count !=matrix_size[0] or matrix_size[0] != matrix_size[1]:
        basic.outputlogMessage('the size of list and matrix do not agree')
        return False
    remain_polygons = list(range(0,count))
    for i in remain_polygons:
        if i < 0:
            continue
        index = [i]
        seed_index = [i]

        while(len(seed_index)>0):
            # set no new find
            new_find_index = []
            for seed in seed_index:
                i_adja = numpy.where(adjacent_matrix[seed,:]==1)
                new_find_index.extend(i_adja[0])

            # to be unique, because one polygon has several adjacent polygon
            new_find_index = numpy.unique(new_find_index).tolist()
            seed_index = []
            for new_value in new_find_index:
                if new_value not in index:
                    seed_index.append(new_value)
            index.extend(seed_index)

        print(i,index)
        for loc in index:
            remain_polygons[loc] = -1
        # merge polygons connected to each other
        if len(index) >1:
            # in my test data, the holes disappear in result. When the number of polygon is small, it work well
            # but when the number is large, the problem occurs.
            # try to merged them one by one
            touched_polygons = [polygon_list[loc] for loc in index]
            union_result = cascaded_union(touched_polygons)
            # union_result = touched_polygons[0]
            # for loc in range(1,len(touched_polygons)):
            #     union_result = cascaded_union([union_result,touched_polygons[loc]])
        else:
            union_result =  polygon_list[index[0]]
            # print(union_result)
        merged_polygons.append(union_result)

    return merged_polygons


def find_adjacent_polygons(polygon1, polygon2):
    """
    decide whether this two polygons are adjacent (share any same point)
    :param polygon1: polygon 1
    :param polygon2: polygon 2
    :return: True if they touch, False otherwise
    """
    try:
        # result = polygon1.touches(polygon2)
        # # two polygon share one line, then consider they are adjacent.
        # # if only share one point, then consider they are not adjacent.
        # if result is True:
        #     line = polygon1.intersection(polygon2)
        #     print( line.length , line.area )
        #     if line.length > 0:
        #         return True
        #     else:
        #         return False
        # tmp1 = polygon1.buffer(0.1)
        # tmp2 = polygon2.buffer(0.1)

        # due to use buffer can enlarge polygon, so the adjacent polygon not touch, they have overlay
        result = polygon1.intersection(polygon2)
        # print(result.length, result.area)
        if result.length > 0 or result.area > 0:
            return True
        else:
            return False


    except:
        # print("Unexpected error:", sys.exc_info()[0])
        basic.outputlogMessage('failed in touch polygon1 (valid %s) and polygon2 (valid %s)'%(polygon1.is_valid,polygon2.is_valid))
        # find whether they have shared points


        # assert False
        return False


def build_adjacent_map_of_polygons(polygons_list):
    """
    build an adjacent matrix of the tou
    :param polygons_list: a list contains all the shapely (not pyshp) polygons
    :return: a matrix storing the adjacent (shared points) for all polygons
    """
    polygon_count = len(polygons_list)
    if polygon_count < 2:
        basic.outputlogMessage('error, the count of polygon is less than 2')
        return False

    ad_matrix = numpy.zeros((polygon_count, polygon_count),dtype=numpy.int8)
    # ad_matrix= ad_matrix.astype(int)
    for i in range(0,polygon_count):
        # print(i, polygons_list[i].is_valid)
        if polygons_list[i].is_valid is False:
            polygons_list[i] = polygons_list[i].buffer(0.1)  # trying to solve self-intersection
        for j in range(i+1,polygon_count):
            # print(i,j,polygons_list[i].is_valid,polygons_list[j].is_valid)
            if polygons_list[j].is_valid is False:
                polygons_list[j] = polygons_list[j].buffer(0.1)  # trying to solve self-intersection
            if find_adjacent_polygons(polygons_list[i],polygons_list[j]) is True:
                # print(i,j)
                ad_matrix[i,j] = 1
                ad_matrix[j,i] = 1  # also need the low part of matrix, or later polygon can not find previous neighbours
    # print(ad_matrix)
    return ad_matrix



def merge_touched_polygons_in_shapefile(shape_file,out_shp):
    """
    merge touched polygons by using sharply function based on GEOS library
    :param shape_file: input shape file path
    :param output:  output shape file path
    :return: True if successful, False otherwise
    """
    if io_function.is_file_exist(shape_file) is False:
        return False

    try:
        org_obj = shapefile.Reader(shape_file)
    except:
        basic.outputlogMessage(str(IOError))
        return False

    # Create a new shapefile in memory
    w = shapefile.Writer()
    w.shapeType = org_obj.shapeType

    org_records = org_obj.records()
    if (len(org_records) < 1):
        basic.outputlogMessage('error, no record in shape file ')
        return False

    # Copy over the geometry without any changes
    w.field('id')
    shapes_list = org_obj.shapes()

    # polygon1 = Polygon(shapes_list[5].points)
    # polygon2 = Polygon(shapes_list[6].points)
    # # polygon2 = Polygon([(0, 0), (3, 10), (3, 0)])
    # polygons = [polygon1, polygon2]
    # u = cascaded_union(polygons)

    polygon_shapely = []
    for temp in shapes_list:
        polygon_shapely.append(shape_from_pyshp_to_shapely(temp))
    #test save polygon with holes
    # merge_result = polygon_shapely

    adjacent_matrix = build_adjacent_map_of_polygons(polygon_shapely)

    if adjacent_matrix is False:
        return False
    merge_result = merge_touched_polygons(polygon_shapely,adjacent_matrix)

    b_keep_holse = parameters.get_b_keep_holes()
    pyshp_polygons = [shape_from_shapely_to_pyshp(shapely_polygon,keep_holes=b_keep_holse) for shapely_polygon in merge_result ]
    # test
    # pyshp_polygons = [shape_from_shapely_to_pyshp(merge_result[0])]

    for i in range(0,len(pyshp_polygons)):
        w._shapes.append(pyshp_polygons[i])
        w.record(i)
    #
    # copy prj file
    org_prj = os.path.splitext(shape_file)[0] + ".prj"
    out_prj = os.path.splitext(out_shp)[0] + ".prj"
    io_function.copy_file_to_dst(org_prj, out_prj,overwrite=True)
    #
    # overwrite original file
    w.save(out_shp)

    # add area, perimeter to shapefile

    # caluclate the area, perimeter
    merge_polygons = [shape_from_pyshp_to_shapely(temp) for temp in pyshp_polygons ]
    area, perimeter = get_area_length_geometric_properties(merge_polygons)

    if len(area)>0 and len(perimeter) > 0:
        shp_obj = shape_opeation()
        shp_obj.add_one_field_records_to_shapefile(out_shp,area,'INarea')
        shp_obj.add_one_field_records_to_shapefile(out_shp, perimeter, 'INperimete')
        shp_obj = None

    return True

def save_shaply_polygon_to_file(polyong_list, file_path):


    pass


def IoU(polygon1,polygon2):
    """
    calculate IoU (intersection over union ) of two polygon
    :param polygon1: polygon 1 of shaply object
    :param polygon2: polygon 2 of shaply object
    :return: IoU value [0, 1], Flase Otherwise
    """

    # # plot shape for checking
    # from matplotlib import pyplot as plt
    # from descartes import PolygonPatch
    # from math import sqrt
    # # from shapely.geometry import Polygon, LinearRing
    # # from shapely.ops import cascaded_union
    # BLUE = '#6699cc'
    # GRAY = '#999999'
    #
    # # plot these two polygons separately
    # fig = plt.figure(1,  dpi=90) #figsize=SIZE,
    # ax = fig.add_subplot(111)
    # poly1patch = PolygonPatch(polygon1, fc=BLUE, ec=BLUE, alpha=0.5, zorder=2)
    # # poly2patch = PolygonPatch(polygon2, ec=BLUE, alpha=0.5, zorder=2)
    # ax.add_patch(poly1patch)
    # # ax.add_patch(poly2patch)
    # boundary = polygon1.bounds
    # xrange = [boundary[0], boundary[2]]
    # yrange = [boundary[1], boundary[3]]
    # ax.set_xlim(*xrange)
    # # ax.set_xticks(range(*xrange) + [xrange[-1]])
    # ax.set_ylim(*yrange)
    # # ax.set_yticks(range(*yrange) + [yrange[-1]])
    # # ax.set_aspect(1)
    #
    # plt.show()

    intersection = polygon1.intersection(polygon2)
    if intersection.is_empty is True:
        return 0.0

    union = polygon1.union(polygon2)

    return intersection.area/union.area

def max_IoU_score(polygon, polygon_list):
    """
    get the IoU score of one polygon compare to many polygon (validation polygon)
    :param polygon: the detected polygon
    :param polygon_list: a list contains training polygons
    :return: the max IoU score, False otherwise
    """
    max_iou = 0.0
    for training_polygon in polygon_list:
        temp_iou = IoU(polygon,training_polygon)
        if temp_iou > max_iou:
            max_iou = temp_iou
    return max_iou

def calculate_IoU_scores(result_shp,val_shp):
    """
    calculate the IoU score of polygons in shape file
    :param result_shp: result shape file contains detected polygons
    :param val_shp: shape file contains validation polygons
    :return: a list contains the IoU of all the polygons
    """
    if io_function.is_file_exist(result_shp) is False or io_function.is_file_exist(val_shp) is False:
        return False

    try:
        result_obj = shapefile.Reader(result_shp)
    except:
        basic.outputlogMessage(str(IOError))
        return False
    try:
        val_obj = shapefile.Reader(val_shp)
    except:
        basic.outputlogMessage(str(IOError))
        return False

    result_polygon_list = result_obj.shapes()
    val_polygon_list = val_obj.shapes()

    if (len(result_polygon_list) < 1):
        basic.outputlogMessage('error, no detected polygon in %s'%result_shp)
        return False
    if (len(val_polygon_list) < 1):
        basic.outputlogMessage('error, no detected polygon in %s'%val_shp)
        return False

    result_polygon_shapely = []
    for temp in result_polygon_list:
        shaply_obj = shape_from_pyshp_to_shapely(temp)
        shaply_obj = shaply_obj.buffer(0.01)  # buffer (0) solve the self-intersection problem, but don't know how it work
        result_polygon_shapely.append(shaply_obj)

    val_polygon_shapely = []
    for temp in val_polygon_list:
        shaply_obj = shape_from_pyshp_to_shapely(temp)
        shaply_obj = shaply_obj.buffer(0)  # buffer (0) solve the self-intersection problem
        val_polygon_shapely.append(shaply_obj)
    #
    # for temp in result_polygon_shapely:
    #     # temp = temp.buffer(0.0)
    #     print('result',temp.is_valid)
    #
    # for temp in val_polygon_shapely:
    #     # temp = temp.buffer(0.0)
    #     print('val',temp.is_valid)

    #output shp


    IoU_socres = []
    index = 0
    for result_polygon in result_polygon_shapely:
        index = index + 1
        iou = max_IoU_score(result_polygon,val_polygon_shapely)
        print(index, iou)
        IoU_socres.append(iou)

    return IoU_socres


def test(input,output):

    operation_obj = shape_opeation()
    # operation_obj.get_polygon_shape_info(input,output)

    # save_shp = "saved.shp"
    # operation_obj.add_fields_shape(input,output,save_shp)

    # operation_obj.add_fields_from_raster(input,output,"color")

    # operation_obj.remove_shape_baseOn_field_value(input,output)
    # operation_obj.remove_nonclass_polygon(input, output,'svmclass')
    # merge_touched_polygons_in_shapefile(input,output)

    result_shp = '/Users/huanglingcao/Data/eboling/eboling_uav_images/dom/output.shp'
    val_shp = '/Users/huanglingcao/Data/eboling/training_validation_data/gps_rtk/gps_rtk_polygons_2.shp'
    # result_shp = "/Users/huanglingcao/Data/eboling/training_validation_data/gps_rtk/result_iou_test2.shp"
    # val_shp = "/Users/huanglingcao/Data/eboling/training_validation_data/gps_rtk/val_iou_test2.shp"
    #
    # # result_shp = "/Users/huanglingcao/Data/eboling/training_validation_data/gps_rtk/result_iou.shp"
    # # val_shp = "/Users/huanglingcao/Data/eboling/training_validation_data/gps_rtk/val_iou.shp"
    iou_score = calculate_IoU_scores(result_shp,val_shp)
    # # print (iou_score)

    operation_obj = None

    pass

def test_get_attribute_value(input,parameter_file):
    if io_function.is_file_exist(parameter_file) is False:
        return False
    attributes_names = parameters.get_attributes_used(parameter_file)
    operation_obj = shape_opeation()
    attributes_values = operation_obj.get_shape_records_value(input, attributes=attributes_names)
    if attributes_values is not False:
        out_file = 'attribute_value.txt'
        operation_obj.save_attributes_values_to_text(attributes_values, out_file)

    operation_obj = None


def main(options, args):
    # if len(args) != 2:
    #     basic.outputlogMessage('error, the number of input argument is 2')
    #     return False

    if options.para_file is None:
        basic.outputlogMessage('warning, no parameters file ')
    else:
        parameters.set_saved_parafile_path(options.para_file)

    input = args[0]
    output = args[1]
    test(input,output)


    pass


if __name__=='__main__':
    usage = "usage: %prog [options] input_path output_file"
    parser = OptionParser(usage=usage, version="1.0 2016-10-26")
    parser.add_option("-p", "--para",
                      action="store", dest="para_file",
                      help="the parameters file")
    # parser.add_option("-s", "--used_file", action="store", dest="used_file",
    #                   help="the selectd used files,only need when you set --action=2")
    # parser.add_option('-o', "--output", action='store', dest="output",
    #                   help="the output file,only need when you set --action=2")

    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 2:
        parser.print_help()
        sys.exit(2)
    main(options, args)
