import dpdata
mddata=dpdata.LabeledSystem('./',cp2k_output_name="SiO2_crystallisation_melt_3DSF_pbe.out",fmt='cp2kdata/md')
print(mddata)
mddata.to_deepmd_npy('./dp_wrap/',fmt='deepmd-npy')
