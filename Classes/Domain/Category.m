//
//  Category.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "Category.h"
#import "Database.h"
#import "Statement.h"
#import "Configuration.h"

@implementation Category

- (NSInteger)count
{
	if ([Configuration configuration].showCompleted)
		[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT COUNT(*) AS total FROM AllTask LEFT JOIN TaskHasCategory ON id=idTask WHERE idCategory=%d", objectId]] execWithTarget:self action:@selector(setCount:)];
	else
		[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT COUNT(*) AS total FROM AllTask LEFT JOIN TaskHasCategory ON id=idTask WHERE idCategory=%d AND completionDate IS NULL", objectId]] execWithTarget:self action:@selector(setCount:)];

	return taskCount;
}

- (void)setCount:(NSDictionary *)dict
{
	taskCount = [[dict objectForKey:@"total"] intValue];
}

@end
