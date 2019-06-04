/*
 *      Author: Guannan Ma
 *      @mythmgn
 */

#include <sys/types.h>
#include <unistd.h>
#include <sys/wait.h>
#include <stdio.h>
#include <stdlib.h>

int isRunUnderRoot(){                                                                                 
    if(geteuid() != 0){                                                                                
        return 0;                                                                                  
    }else{                                                                                             
        return 1;                                                                                   
    }                                                                                                  
} 

int runNewProcess(char *pFolder, char* pName){
	pid_t child;
	if( (child=fork()) < 0 ){
		exit(EXIT_FAILURE);
	}
	else if (child ==0){
	/*child process*/
		FILE *in;
		char pExe[2056];
		char buff[1024];
        int status;
		sprintf(pExe, "cd %s && %s", pFolder, pName);
        setuid(geteuid());
		if(!(in = popen(pExe, "r"))){
			exit(EXIT_FAILURE);
		}
		while(fgets(buff, sizeof(buff), in)!=NULL){
			printf("%s", buff);
		}
		status = pclose(in);
        if (0!=status)
            exit(WEXITSTATUS(status));
        else
            exit(EXIT_SUCCESS);
	}else{
	/*parent process*/
		int status;
		if( child!=waitpid(child, &status, 0) || WEXITSTATUS(status)!=EXIT_SUCCESS){
			fprintf(stderr, "Error when check waitpid and WEXITSTATUS\n");
			return WEXITSTATUS(status);
		}
		return EXIT_SUCCESS;
	}
}

int main(int argc, char **argv){
	if(0==isRunUnderRoot()){
		fprintf(stderr,"Elavator does not run under +S attribute. Exiting....\n");
		return EXIT_FAILURE;
	}
	exit(runNewProcess("./", "env python ./euid_backup.py"));
}
