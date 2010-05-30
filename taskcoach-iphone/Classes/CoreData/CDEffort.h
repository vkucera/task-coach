//
//  CDEffort.h
//  
//
//  Created by Jérôme Laheurte on 30/05/10.
//  Copyright 2010 __MyCompanyName__. All rights reserved.
//

#import <CoreData/CoreData.h>
#import "CDDomainObject.h"

@class CDTask;

@interface CDEffort :  CDDomainObject  
{
}

@property (nonatomic, retain) NSDate * started;
@property (nonatomic, retain) NSDate * ended;
@property (nonatomic, retain) CDTask * task;

@end



