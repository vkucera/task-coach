//
//  DomainObject.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

#define STATUS_NONE               0
#define STATUS_NEW                1
#define STATUS_MODIFIED           2
#define STATUS_DELETED            3

@interface DomainObject : NSObject
{
	NSInteger objectId;
	NSNumber *fileId;
	NSString *name;
	NSInteger status;
	NSString *taskCoachId;
}

@property (nonatomic, readonly) NSInteger objectId;
@property (nonatomic, retain, readonly) NSNumber *fileId;
@property (nonatomic, retain) NSString *name;
@property (nonatomic, readonly) NSInteger status;
@property (nonatomic, copy) NSString *taskCoachId;

- initWithId:(NSInteger)ID fileId:(NSNumber *)fileId name:(NSString *)name status:(NSInteger)status taskCoachId:(NSString *)taskCoachId;

- (void)setStatus:(NSInteger)status;
- (void)delete;

- (void)bind;
- (void)save;

@end
