c ph2dt.inc: Stores parameters that define array dimensions in ph2dt.
c            Modify to fit size of problem and available computer memory.
c Parameter Description:
c MEV:   Max number of events.
c MSTA:  Max number of stations.
c MOBS:  Max number of phases (P&S) per eventer event.

	integer	MEV, MSTA, MOBS

c mediuam size problem
c	parameter(MEV=    32000,    
	parameter(MEV=    16000,    
     &		MSTA=   2400,		
     &		MOBS=   500)

cc large size problem
c	parameter(MEV=    44800,    
c     &	 	MSTA=   830,		
c     &		MOBS=   500)
