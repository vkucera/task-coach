//
//  CDDomainObject+Addons.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 30/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "CDDomainObject.h"

#define STATUS_NONE               0
#define STATUS_NEW                1
#define STATUS_MODIFIED           2
#define STATUS_DELETED            3

@interface CDDomainObject (Addons)

- (BOOL)save;

- (void)updateStatus:(NSInteger)status;
- (void)markDirty;
- (void)delete;

@end
