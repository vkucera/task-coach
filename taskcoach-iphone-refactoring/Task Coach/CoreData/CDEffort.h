//
//  CDEffort.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 13/03/11.
//  Copyright (c) 2011 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>
#import "CDDomainObject.h"

@class CDTask;

@interface CDEffort : CDDomainObject {
@private
}
@property (nonatomic, retain) NSDate * started;
@property (nonatomic, retain) NSDate * ended;
@property (nonatomic, retain) CDTask * task;

@end
