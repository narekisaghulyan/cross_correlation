set MODULE cc_testbench
start $MODULE
add wave $MODULE/*
add wave $MODULE/cc_test/*
run 10000us
