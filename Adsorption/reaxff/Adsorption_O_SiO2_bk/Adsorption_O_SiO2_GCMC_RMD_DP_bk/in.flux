variable Ts equal 500 
variable seed equal 29322
variable seed_int equal ceil(random(0,99999999,${seed}))
variable cx file ${Ts}_vx.dat
variable cy file ${Ts}_vy.dat
variable cz file ${Ts}_vz.dat
units metal 
#atom_style charge
boundary p p f
read_data nve.lmp
#read_data slab_dp.lmp extra/atom/types 1
#mass 3 15.999
velocity all set 0 0 0
#set group all charge 0
#pair_style reaxff NULL safezone 3 
#pair_coeff * * ffield.reax Si O O
#fix gsi_qeq all qeq/reaxff 1 0  10 1e-6 reaxff  
pair_style      deepmd graph_compressed_20241109_clean_2.pb
pair_coeff      * * Si O O
#####set region 
region bottom block INF INF INF INF 0 2 
region thermo_region block INF INF INF INF 2 5
region surf block INF INF INF INF 5 INF  
group surf dynamic all region surf every 100
group thermo_atoms dynamic all region thermo_region every 100
group fixwall region bottom 
fix 1 fixwall setforce 0 0 0 
group move subtract all fixwall 
velocity move create ${Ts} ${seed_int} rot yes mom yes dist gaussian 
#####relax 
variable dt equal 0.00025
timestep ${dt}
fix re_thermo move nvt temp ${Ts} ${Ts} $(100*dt)
compute 1 move temp 
compute 2 surf temp 
compute 3 thermo_atoms temp

fix_modify re_thermo temp 1
thermo 500
thermo_style custom step temp c_1 c_2 pe ke etotal 
thermo_modify lost ignore flush yes
#run 10000
#write_data nvt.lmp 
unfix re_thermo
fix re_nve move nve
#run 10000
#write_data nve.lmp 
unfix re_nve
reset_timestep  0 
#####add_loop
variable dt equal 0.0001
timestep  ${dt}
variable insert_z equal 16+10
variable del_z equal ${insert_z}+5
region insert_region block INF INF INF INF ${insert_z} ${insert_z}
region del_region block INF INF INF INF ${del_z} INF
#dump 1 all custom 5000 all.lammpstrj  id type x y z vx vy vz element q 
dump 1 all custom 5000 zz_all_500k.lammpstrj  id type x y z vx vy vz element
dump_modify 1 element Si O O 
variable  dt_insert equal ceil(0.568/${dt})
variable dn equal 0
variable Ntotal equal ceil(5000/0.568)
variable N_add loop ${Ntotal} 
variable TE equal ${TS}+0.05
fix thermostat thermo_atoms  nvt temp ${Ts} ${TE} $(100*dt)
fix_modify thermostat temp 3 
fix gsi_nve surf nve
#dump 2 surf custom 1000 traj/surf.*.lammpstrj id type x y z vx vy vz element q
dump 2 surf custom 1000 traj/surf.*.lammpstrj id type x y z vx vy vz element
dump_modify 2 element Si O O
label add_loop
print "insert_numbers : ${N_add}"
create_atoms 3 random 1 ${seed_int} insert_region overlap 2.5 maxtry 200 
group insert_atom region insert_region
velocity insert_atom set ${cx} ${cy} ${cz}
next cx 
next cy 
next cz
group insert_atom delete
group del_atoms region del_region
variable num_del equal count(del_atoms)
if "${num_del} > 0 " then &
"write_dump del_atoms custom del_atoms/dump.*.lammpstrj id type x y z vx vy vz " &
#"set group all charge 0" &
"delete_atoms group del_atoms compress no" 
group del_atoms delete
run ${dt_insert}
next N_add
variable TS equal ${TE}
jump SELF add_loop
write_restart r1.restart 
write_data  r1.lmp
