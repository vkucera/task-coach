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
@property (nonatomic, retain) NSSet* category;
@property (nonatomic, retain) NSSet* effort;

@end


@interface CDTask (CoreDataGeneratedAccessors)
- (void)addCategoryObject:(CDCategory *)value;
- (void)removeCategoryObject:(CDCategory *)value;
- (void)addCategory:(NSSet *)value;
- (void)removeCategory:(NSSet *)value;

- (void)addEffortObject:(CDEffort *)value;
- (void)removeEffortObject:(CDEffort *)value;
- (void)addEffort:(NSSet *)value;
- (void)removeEffort:(NSSet *)value;

@end

