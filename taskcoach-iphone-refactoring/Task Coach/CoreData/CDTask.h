//
//  CDTask.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 13/03/11.
//  Copyright (c) 2011 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>
#import "CDHierarchicalDomainObject.h"

@class CDCategory, CDEffort;

@interface CDTask : CDHierarchicalDomainObject {
@private
}
@property (nonatomic, retain) NSNumber * recRepeat;
@property (nonatomic, retain) NSDate * dueDate;
@property (nonatomic, retain) NSDate * reminderDate;
@property (nonatomic, retain) NSNumber * recSameWeekday;
@property (nonatomic, retain) NSNumber * priority;
@property (nonatomic, retain) NSNumber * dateStatus;
@property (nonatomic, retain) NSNumber * recPeriod;
@property (nonatomic, retain) NSString * longDescription;
@property (nonatomic, retain) NSDate * startDate;
@property (nonatomic, retain) NSDate * completionDate;
@property (nonatomic, retain) NSSet* categories;
@property (nonatomic, retain) NSSet* efforts;

@end
