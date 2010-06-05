//
//  CDTask.h
//  
//
//  Created by Jérôme Laheurte on 05/06/10.
//  Copyright 2010 __MyCompanyName__. All rights reserved.
//

#import <CoreData/CoreData.h>
#import "CDHierarchicalDomainObject.h"

@class CDCategory;
@class CDEffort;

@interface CDTask :  CDHierarchicalDomainObject  
{
}

@property (nonatomic, retain) NSDate * reminderDate;
@property (nonatomic, retain) NSDate * completionDate;
@property (nonatomic, retain) NSDate * startDate;
@property (nonatomic, retain) NSNumber * dateStatus;
@property (nonatomic, retain) NSString * longDescription;
@property (nonatomic, retain) NSDate * dueDate;
@property (nonatomic, retain) NSSet* categories;
@property (nonatomic, retain) NSSet* efforts;

@end


@interface CDTask (CoreDataGeneratedAccessors)
- (void)addCategoriesObject:(CDCategory *)value;
- (void)removeCategoriesObject:(CDCategory *)value;
- (void)addCategories:(NSSet *)value;
- (void)removeCategories:(NSSet *)value;

- (void)addEffortsObject:(CDEffort *)value;
- (void)removeEffortsObject:(CDEffort *)value;
- (void)addEfforts:(NSSet *)value;
- (void)removeEfforts:(NSSet *)value;

@end

