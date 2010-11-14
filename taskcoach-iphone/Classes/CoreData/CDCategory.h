//
//  CDCategory.h
//  
//
//  Created by Jérôme Laheurte on 14/11/10.
//  Copyright 2010 __MyCompanyName__. All rights reserved.
//

#import <CoreData/CoreData.h>
#import "CDHierarchicalDomainObject.h"

@class CDTask;

@interface CDCategory :  CDHierarchicalDomainObject  
{
}

@property (nonatomic, retain) NSSet* task;

@end


@interface CDCategory (CoreDataGeneratedAccessors)
- (void)addTaskObject:(CDTask *)value;
- (void)removeTaskObject:(CDTask *)value;
- (void)addTask:(NSSet *)value;
- (void)removeTask:(NSSet *)value;

@end

