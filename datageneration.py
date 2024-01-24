from PIL import Image
import numpy as np
import cv2
from math import ceil, sqrt, floor
from bfio import BioWriter
from pathlib import Path, PurePath

class DatasetGenerator:
    def __init__(self,  
                    image_int_dir, 
                    image_seg_dir,
                    base_mask_image_path,
                    base_intensity_image_path) -> None:
        self._image_int_dir = Path(image_int_dir)
        self._image_seg_dir = Path(image_seg_dir)
        self._base_mask_image_path = Path(base_mask_image_path)
        self._base_intensity_image_path = Path(base_intensity_image_path)
        self._roi_base_data = None

    def local_to_global_coord(self, local_tile_x_index, local_tile_y_index, local_x, local_y, tile_x_size, tile_y_size):
        global_x = local_tile_x_index*tile_x_size + local_x 
        global_y = local_tile_y_index*tile_y_size + local_y 
        return (global_x, global_y)

    def global_to_local_coord(self, x, y, tile_x_size, tile_y_size):    
        roi_tile_x_index = int(x / tile_x_size)
        roi_tile_y_index = int(y / tile_y_size)

        image_x_offset = tile_x_size*roi_tile_x_index
        image_y_offset = tile_y_size*roi_tile_y_index
        
        roi_local_x = x - image_x_offset
        roi_local_y = y - image_y_offset
        
        return ((roi_tile_x_index, roi_tile_y_index), (roi_local_x, roi_local_y))
    
    def tile_seg_id (self, tile_x_index, tile_y_index, global_x_size, tile_x_size):
        num_roi_tiles_along_image_width = ceil(global_x_size/tile_x_size)
        seg_id = num_roi_tiles_along_image_width*(tile_y_index)+tile_x_index+1
        return seg_id

    def fill_tile(self, tile_x_index, tile_y_index, tile_x_size, tile_y_size, image_height, image_width, roi_height, roi_width, roi_base_data, padding, oversized_rois, num_oversized_diag_rois):
        tile_data = np.zeros((tile_y_size, tile_x_size), dtype=np.uint32)
        #top left point
        (g_x, g_y) = self.local_to_global_coord(tile_x_index, tile_y_index, 0, 0, tile_x_size, tile_y_size)
        ((r_x_ind, r_y_ind), (r_x_l, r_y_l)) =  self.global_to_local_coord(g_x, g_y, roi_width, roi_height)
        top_left_roi_tile = (r_x_ind, r_y_ind) 
        left_edge_tile_x_ind = r_x_ind
        top_edge_tile_y_ind = r_y_ind
        left_edge_roi_local_x_coord = r_x_l
        top_edge_roi_local_y_coord = r_y_l
        
        #bottom right point
        (g_x, g_y) = self.local_to_global_coord(tile_x_index, tile_y_index, tile_x_size-1, tile_y_size-1, tile_x_size, tile_y_size)
        ((r_x_ind, r_y_ind), (r_x_l, r_y_l)) =  self.global_to_local_coord(g_x, g_y, roi_width, roi_height)
        bottom_right_roi_tile = (r_x_ind, r_y_ind) 
        right_edge_tile_x_ind = r_x_ind
        bottom_edge_tile_y_ind = r_y_ind
        right_edge_roi_local_x_coord = r_x_l
        bottom_edge_roi_local_y_coord = r_y_l
        
        for roi_tile_x in range(top_left_roi_tile[0],bottom_right_roi_tile[0]+1):
            for roi_tile_y in range(top_left_roi_tile[1],bottom_right_roi_tile[1]+1):
                seg_id = self.tile_seg_id(roi_tile_x, roi_tile_y, image_width, roi_width)
                # start with assuming the whole roi tile can be inside the image tile,
                # and then crop as follows
                roi_left_x = 0
                roi_top_y = 0
                roi_right_x = roi_width-1
                roi_bottom_y = roi_height-1
                # if the tile is on the left edge, we know x_start
                if roi_tile_x == left_edge_tile_x_ind:
                    roi_left_x = left_edge_roi_local_x_coord
                # if the tile is on the right edge, we know x_end
                if roi_tile_x == right_edge_tile_x_ind:
                    roi_right_x = right_edge_roi_local_x_coord            
                # if the tile is on top edge, we know y_start
                if roi_tile_y == top_edge_tile_y_ind:
                    roi_top_y = top_edge_roi_local_y_coord            
                # if the tile is on bottom edge, we know y_end
                if roi_tile_y == bottom_edge_tile_y_ind:
                    roi_bottom_y = bottom_edge_roi_local_y_coord            
                # now find out image tile coordinate for the the roi tiled crop portion and 
                # copy the data

                # convert roi_local to image coord 
                (i_x_1, i_y_1) = self.local_to_global_coord(roi_tile_x, roi_tile_y, roi_left_x, roi_top_y, roi_width, roi_height)
                (i_x_2, i_y_2) = self.local_to_global_coord(roi_tile_x, roi_tile_y, roi_right_x, roi_bottom_y, roi_width, roi_height)
                # now from image_coord to tile_coord                
                ((tmp_1, tmp_2), (t_x_l_1, t_y_l_1)) = self.global_to_local_coord(i_x_1, i_y_1, tile_x_size, tile_y_size)
                ((tmp_1, tmp_2), (t_x_l_2, t_y_l_2)) = self.global_to_local_coord(i_x_2, i_y_2, tile_x_size, tile_y_size)
                

                if roi_tile_x == roi_tile_y and oversized_rois and roi_tile_x < num_oversized_diag_rois:
                    shift = padding
                    roi_base_data_new = roi_base_data.copy()
                    mid_x = int((roi_width)/2)
                    mid_y = int((roi_height)/2)
                    roi_base_data_new[:, 0:mid_x+1-shift] = roi_base_data_new[:, shift:mid_x+1] 
                    roi_base_data_new[:, mid_x+shift:roi_width] = roi_base_data_new[:, mid_x:roi_width-shift] 
                    roi_base_data_new[0:mid_y+1-shift, :] = roi_base_data_new[shift:mid_y+1, :] 
                    roi_base_data_new[mid_y+shift:roi_height, :] = roi_base_data_new[mid_y:roi_height-shift, :] 
                    tile_data[t_y_l_1:t_y_l_2+1, t_x_l_1:t_x_l_2+1] = seg_id*roi_base_data_new[roi_top_y:roi_bottom_y+1, roi_left_x:roi_right_x+1]
                else:
                    tile_data[t_y_l_1:t_y_l_2+1, t_x_l_1:t_x_l_2+1 ] = seg_id*roi_base_data[roi_top_y:roi_bottom_y+1,roi_left_x:roi_right_x+1]

        return tile_data


    def read_mask_image(self, roi_size, padding):
        #read mask image
        cat_img = Image.open(self._base_mask_image_path)
        #crop image
        tmp = np.asarray(cat_img)
        image_data = tmp[:]
        ret, im = cv2.threshold(image_data, 100, 255, cv2.THRESH_BINARY_INV)
        contours, hierarchy  = cv2.findContours(im, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        x,y,w,h = cv2.boundingRect(contours[0])
        cropped_image = cat_img.crop((x,y,x+w,y+h))

        #resize image to match roi area
        resized_image_size = ceil(1.44*roi_size)
        w_r = ceil(sqrt(resized_image_size*w/h))
        h_r = ceil(resized_image_size/w_r)
        resized_image = cropped_image.resize((w_r, h_r))

        #pad image
        w_r_n = w_r + 2*padding
        h_r_n = h_r + 2*padding
        resized_image_w_padding = Image.new(resized_image.mode, (w_r_n, h_r_n), 255)
        resized_image_w_padding.paste(resized_image,(padding,padding))
        final_image_data = np.asarray(resized_image_w_padding)
        ret, roi_base_data_orig = cv2.threshold(final_image_data[:], 100,1, cv2.THRESH_BINARY_INV)
        self._roi_base_data = roi_base_data_orig.astype(np.uint32)


    def generate_image_pair(self, n_rois, roi_size, padding, percent_oversized_diag_rois=0):
        self.read_mask_image(roi_size, padding)
        # find roi tile count
        n_rois_x = ceil(sqrt(n_rois))
        n_rois_y = floor(sqrt(n_rois))

        num_diag_rois = ceil(sqrt(n_rois_x**2 + n_rois_y**2))
        requested_oversized_rois = int(n_rois_x*n_rois_y*percent_oversized_diag_rois/100)
        if num_diag_rois < requested_oversized_rois:
            num_oversized_diag_rois = num_diag_rois
        else:
            num_oversized_diag_rois = requested_oversized_rois

        # full image dims
        image_width = n_rois_x*self._roi_base_data.shape[1]
        image_height = n_rois_y*self._roi_base_data.shape[0]
        # roi dims
        roi_width = self._roi_base_data.shape[1]
        roi_height = self._roi_base_data.shape[0]
        
        tile_x_size = 1024
        tile_y_size = 1024
        seg_file_name = PurePath(self._image_seg_dir, Path(f"synthetic_nrois={n_rois}_roiarea={roi_size}.ome.tif")) 
        with BioWriter(seg_file_name, max_workers=4, backend='python', X=image_width, Y=image_height, Z=1, C=1, T=1, dtype=np.uint32) as bw:
            tile_y_ind = 0
            for y in range(0,image_height, tile_y_size):
                tile_x_ind = 0
                y_max = min([image_height,y+tile_y_size])
                for x in range(0, image_width, tile_x_size):
                    x_max = min([image_width,x+tile_x_size])
                    tmp = self.fill_tile(tile_x_ind, tile_y_ind, tile_x_size, tile_y_size, image_height, image_width, roi_height, roi_width, self._roi_base_data, padding, True, num_oversized_diag_rois)
                    bw[y:y_max, x:x_max,0,0,0] = tmp[:y_max-y, :x_max-x]
                    tile_x_ind = tile_x_ind+1
                tile_y_ind = tile_y_ind+1
            
        # now generate int image

        # crop intensity image
        star_img = Image.open(self._base_intensity_image_path)
        tmp = np.asarray(star_img)
        int_data = tmp[:,:,0]

        r = floor (int_data.shape[0] / 2);
        sq_side = floor (2 * r / sqrt(2))
        x_offset = int((int_data.shape[0] -sq_side)/2)
        y_offset = x_offset

        cropped_image_orig = int_data[x_offset:x_offset+sq_side,y_offset:y_offset+sq_side]
        cropped_image = cropped_image_orig.astype(np.uint32)
        int_file_name = PurePath(self._image_int_dir, Path(f"synthetic_nrois={n_rois}_roiarea={roi_size}.ome.tif"))
        with BioWriter(int_file_name, max_workers=4, backend='python', X=image_width, Y=image_height, Z=1, C=1, T=1, dtype=np.uint32) as bw:
            tile_y_ind = 0
            for y in range(0,image_height, tile_y_size):
                tile_x_ind = 0
                y_max = min([image_height,y+tile_y_size])
                for x in range(0, image_width, tile_x_size):
                    x_max = min([image_width,x+tile_x_size])
                    tmp = self.fill_tile(tile_x_ind, tile_y_ind, tile_x_size, tile_y_size, image_height, image_width, sq_side, sq_side, cropped_image, padding, False, 0)
                    bw[y:y_max, x:x_max,0,0,0] = tmp[:y_max-y, :x_max-x]
                    tile_x_ind = tile_x_ind+1
                tile_y_ind = tile_y_ind+1