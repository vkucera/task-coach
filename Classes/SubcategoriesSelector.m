//
//  SubcategoriesSelector.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/03/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "SubcategoriesSelector.h"
#import "Category.h"
#import "Database.h"
#import "Statement.h"
#import "String+Utils.h"

@implementation SubcategoriesSelector

- initWithCategory:(NSInteger)categoryId
{
	if (self = [super init])
	{
		categoryIds = [[NSMutableArray alloc] init];

		[categoryIds addObject:[NSString stringWithFormat:@"idCategory=%d", categoryId]];

		[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT id FROM CurrentCategory WHERE parentId=%d", categoryId]] execWithTarget:self action:@selector(onCategory:)];
	}

	return self;
}

- (void)onCategory:(NSDictionary *)dict
{
	[categoryIds addObject:[NSString stringWithFormat:@"idCategory=%@", [dict objectForKey:@"id"]]];

	[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT id FROM CurrentCategory WHERE parentId=%@", [dict objectForKey:@"id"]]] execWithTarget:self action:@selector(onCategory:)];
}

- (NSString *)clause
{
	return [NSString stringWithFormat:@"(%@)", [@" OR " stringByJoiningStrings:categoryIds]];
}

@end
