//
//  CDCategory.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 13/03/11.
//  Copyright (c) 2011 __MyCompanyName__. All rights reserved.
//

#import "CDCategory.h"
#import "CDTask.h"


@implementation CDCategory
@dynamic task;

- (void)addTaskObject:(CDTask *)value {    
    NSSet *changedObjects = [[NSSet alloc] initWithObjects:&value count:1];
    [self willChangeValueForKey:@"task" withSetMutation:NSKeyValueUnionSetMutation usingObjects:changedObjects];
    [[self primitiveValueForKey:@"task"] addObject:value];
    [self didChangeValueForKey:@"task" withSetMutation:NSKeyValueUnionSetMutation usingObjects:changedObjects];
    [changedObjects release];
}

- (void)removeTaskObject:(CDTask *)value {
    NSSet *changedObjects = [[NSSet alloc] initWithObjects:&value count:1];
    [self willChangeValueForKey:@"task" withSetMutation:NSKeyValueMinusSetMutation usingObjects:changedObjects];
    [[self primitiveValueForKey:@"task"] removeObject:value];
    [self didChangeValueForKey:@"task" withSetMutation:NSKeyValueMinusSetMutation usingObjects:changedObjects];
    [changedObjects release];
}

- (void)addTask:(NSSet *)value {    
    [self willChangeValueForKey:@"task" withSetMutation:NSKeyValueUnionSetMutation usingObjects:value];
    [[self primitiveValueForKey:@"task"] unionSet:value];
    [self didChangeValueForKey:@"task" withSetMutation:NSKeyValueUnionSetMutation usingObjects:value];
}

- (void)removeTask:(NSSet *)value {
    [self willChangeValueForKey:@"task" withSetMutation:NSKeyValueMinusSetMutation usingObjects:value];
    [[self primitiveValueForKey:@"task"] minusSet:value];
    [self didChangeValueForKey:@"task" withSetMutation:NSKeyValueMinusSetMutation usingObjects:value];
}


@end
