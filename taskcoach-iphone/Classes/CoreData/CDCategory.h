//
//  CDCategory.h
//  
//
//  Created by Jérôme Laheurte on 30/05/10.
//  Copyright 2010 __MyCompanyName__. All rights reserved.
//

#import <CoreData/CoreData.h>
#import "CDDomainObject.h"

@class CDTask;

@interface CDCategory :  CDDomainObject  
{
}

@property (nonatomic, retain) NSSet* child;
@property (nonatomic, retain) CDCategory * parent;
@property (nonatomic, retain) NSSet* task;

@end


@interface CDCategory (CoreDataGeneratedAccessors)
- (void)addChildObject:(CDCategory *)value;
- (void)removeChildObject:(CDCategory *)value;
- (void)addChild:(NSSet *)value;
- (void)removeChild:(NSSet *)value;

- (void)addTaskObject:(CDTask *)value;
- (void)removeTaskObject:(CDTask *)value;
- (void)addTask:(NSSet *)value;
- (void)removeTask:(NSSet *)value;

@end

