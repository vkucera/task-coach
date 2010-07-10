//
//  EntityUploadState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 05/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "ItemState.h"

@interface EntityUploadState : ItemState
{
	NSArray *objects;
	NSInteger index;
}

- (void)packObject:(NSManagedObject *)object;

- (void)activated;

- (NSString *)entityName;
- (NSInteger)status;

- (NSString *)ordering;

@end
